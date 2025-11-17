"""Chrome DevTools Protocol Manager for Android Chrome automation"""

import asyncio
import json
import logging
from typing import List, Dict, Optional, Any, Coroutine
import websockets
from websockets.client import WebSocketClientProtocol
import aiohttp

logger = logging.getLogger(__name__)


class CDPMessage:
    """Chrome DevTools Protocol message builder"""

    _message_id = 0

    @classmethod
    def get_next_id(cls) -> int:
        """Get next message ID"""
        cls._message_id += 1
        return cls._message_id

    @staticmethod
    def create(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create CDP message

        Args:
            method: CDP method name
            params: Method parameters

        Returns:
            Message dictionary
        """
        return {
            "id": CDPMessage.get_next_id(),
            "method": method,
            "params": params or {}
        }


class ChromeDevToolsManager:
    """Manages Chrome DevTools Protocol communication via WebSocket"""

    DEFAULT_WS_URL = "ws://localhost:9222/devtools/page/1"
    DEFAULT_TIMEOUT = 5.0  # seconds

    def __init__(
        self,
        ws_url: str = DEFAULT_WS_URL,
        timeout: float = DEFAULT_TIMEOUT
    ):
        """
        Initialize Chrome DevTools Manager

        Args:
            ws_url: WebSocket URL for Chrome DevTools
            timeout: Command timeout in seconds
        """
        self.ws_url = ws_url
        self.timeout = timeout
        self.ws: Optional[WebSocketClientProtocol] = None
        self.response_queue: Dict[int, Dict[str, Any]] = {}
        self._running = False
        self._receive_task: Optional[asyncio.Task[None]] = None

    async def connect(self) -> bool:
        """
        Connect to Chrome DevTools

        Returns:
            True if connected successfully
        """
        try:
            # If ws_url doesn't have a specific page ID, discover available pages
            if self.ws_url == self.DEFAULT_WS_URL or "/devtools/page/1" in self.ws_url:
                discovered_url = await self._discover_page()
                if discovered_url:
                    self.ws_url = discovered_url
                    logger.info(f"Discovered Chrome page: {self.ws_url}")

            logger.info(f"Connecting to Chrome DevTools: {self.ws_url}")
            self.ws = await asyncio.wait_for(
                websockets.connect(
                    self.ws_url,
                    max_size=10 * 1024 * 1024  # 10MB limit for large DOM responses
                ),
                timeout=self.timeout
            )
            self._running = True

            # Start message receiver task
            self._receive_task = asyncio.create_task(self._receive_messages())
            logger.info("Successfully connected to Chrome DevTools")
            return True

        except asyncio.TimeoutError:
            logger.error(f"Connection timeout to {self.ws_url}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Chrome DevTools: {e}")
            return False

    async def _discover_page(self) -> Optional[str]:
        """
        Discover available Chrome pages and return WebSocket URL

        Returns:
            WebSocket URL of first available page, or None
        """
        try:
            # Extract host and port from ws_url
            # ws://localhost:9222/devtools/page/1 -> http://localhost:9222
            import re
            match = re.match(r'ws://([^/]+)', self.ws_url)
            if not match:
                return None

            host_port = match.group(1)
            http_url = f"http://{host_port}/json"

            # Query available pages
            async with aiohttp.ClientSession() as session:
                async with session.get(http_url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        pages = await response.json()

                        # Find first page with webSocketDebuggerUrl
                        for page in pages:
                            ws_url = page.get('webSocketDebuggerUrl')
                            if ws_url:
                                logger.info(f"Found page: {page.get('title', 'Unknown')} ({page.get('url', 'Unknown')})")
                                return ws_url

                        logger.warning("No pages with WebSocket URL found")
                    else:
                        logger.warning(f"Failed to query pages: HTTP {response.status}")

            return None

        except Exception as e:
            logger.debug(f"Page discovery failed: {e}")
            return None

    async def disconnect(self) -> None:
        """Disconnect from Chrome DevTools"""
        self._running = False

        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from Chrome DevTools")

    async def _receive_messages(self) -> None:
        """Receive and queue messages from Chrome"""
        try:
            if not self.ws:
                return

            async for message in self.ws:
                try:
                    data = json.loads(message)
                    msg_id = data.get("id")
                    if msg_id:
                        self.response_queue[msg_id] = data
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in message receiver: {e}")

    async def send_command(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        retry: int = 3
    ) -> Dict[str, Any]:
        """
        Send command to Chrome and wait for response with retry logic

        Args:
            method: CDP method name
            params: Command parameters
            retry: Number of retries on connection error

        Returns:
            Response result dictionary

        Raises:
            RuntimeError: If not connected or command fails
            asyncio.TimeoutError: If response times out
        """
        last_error = None

        for attempt in range(retry):
            try:
                if not self.ws or not self._running:
                    # Try to reconnect
                    logger.warning(f"Connection lost, attempting reconnect (attempt {attempt + 1}/{retry})")
                    if not await self.connect():
                        raise RuntimeError("Failed to reconnect to Chrome DevTools")

                msg = CDPMessage.create(method, params)
                msg_id = msg["id"]

                # Send command
                await self.ws.send(json.dumps(msg))

                # Wait for response with timeout
                start_time = asyncio.get_event_loop().time()
                while msg_id not in self.response_queue:
                    if asyncio.get_event_loop().time() - start_time > self.timeout:
                        raise asyncio.TimeoutError(f"No response for {method}")
                    await asyncio.sleep(0.01)

                response = self.response_queue.pop(msg_id)

                if "error" in response:
                    error_msg = response["error"].get("message", "Unknown error")
                    raise RuntimeError(f"CDP Error: {error_msg}")

                return response.get("result", {})

            except (websockets.exceptions.ConnectionClosed,
                    websockets.exceptions.ConnectionClosedError) as e:
                last_error = e
                logger.warning(f"WebSocket connection closed during {method}: {e}")
                self._running = False
                self.ws = None

                if attempt < retry - 1:
                    await asyncio.sleep(1.0)  # Wait before retry
                    continue
                else:
                    raise RuntimeError(f"WebSocket connection failed after {retry} attempts: {e}")

            except asyncio.TimeoutError as e:
                last_error = e
                if attempt < retry - 1:
                    logger.warning(f"Command timeout for {method}, retrying...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    raise asyncio.TimeoutError(f"Command timeout: {method}")

        if last_error:
            raise last_error

    # DOM Commands

    async def get_document(self) -> Dict[str, Any]:
        """
        Get document root node

        Returns:
            Document info with root node
        """
        return await self.send_command("DOM.getDocument")

    async def describe_node(
        self,
        node_id: int,
        depth: int = -1,
        pierce: bool = False
    ) -> Dict[str, Any]:
        """
        Describe a node in detail

        Args:
            node_id: Node ID
            depth: Depth to traverse (-1 for all)
            pierce: Whether to pierce shadow DOM

        Returns:
            Node description
        """
        return await self.send_command("DOM.describeNode", {
            "nodeId": node_id,
            "depth": depth,
            "pierce": pierce
        })

    async def get_node_tree(self, node_id: int, depth: int = -1) -> Dict[str, Any]:
        """
        Get subtree of a node

        Args:
            node_id: Node ID
            depth: Depth to traverse

        Returns:
            Node tree
        """
        return await self.send_command("DOM.describeNode", {
            "nodeId": node_id,
            "depth": depth
        })

    async def query_selector(self, selector: str, node_id: int = 1) -> Optional[int]:
        """
        Query element by CSS selector

        Args:
            selector: CSS selector
            node_id: Starting node ID (default: document)

        Returns:
            Node ID or None
        """
        try:
            result = await self.send_command("DOM.querySelector", {
                "nodeId": node_id,
                "selector": selector
            })
            return result.get("nodeId")
        except Exception as e:
            logger.debug(f"Query selector failed: {e}")
            return None

    async def query_selector_all(self, selector: str, node_id: int = 1) -> List[int]:
        """
        Query all elements by CSS selector

        Args:
            selector: CSS selector
            node_id: Starting node ID (default: document)

        Returns:
            List of node IDs
        """
        try:
            result = await self.send_command("DOM.querySelectorAll", {
                "nodeId": node_id,
                "selector": selector
            })
            return result.get("nodeIds", [])
        except Exception as e:
            logger.debug(f"Query selector all failed: {e}")
            return []

    async def get_attributes(self, node_id: int) -> Dict[str, str]:
        """
        Get element attributes

        Args:
            node_id: Node ID

        Returns:
            Dictionary of attributes
        """
        try:
            result = await self.send_command("DOM.getAttributes", {
                "nodeId": node_id
            })
            # Attributes are flat array: [key1, val1, key2, val2, ...]
            attrs = result.get("attributes", [])
            return {attrs[i]: attrs[i + 1] for i in range(0, len(attrs), 2)}
        except Exception as e:
            logger.debug(f"Get attributes failed: {e}")
            return {}

    async def get_box_model(self, node_id: int) -> Dict[str, Any]:
        """
        Get element box model (coordinates)

        Args:
            node_id: Node ID

        Returns:
            Box model with coordinates
        """
        return await self.send_command("DOM.getBoxModel", {
            "nodeId": node_id
        })

    # Runtime Commands

    async def evaluate_js(
        self,
        expression: str,
        return_by_value: bool = True
    ) -> Any:
        """
        Execute JavaScript and get result

        Args:
            expression: JavaScript code to execute
            return_by_value: Whether to return value (vs reference)

        Returns:
            Evaluation result

        Raises:
            RuntimeError: If JavaScript has error
        """
        result = await self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": return_by_value
        })

        if "exceptionDetails" in result:
            error = result["exceptionDetails"]
            raise RuntimeError(f"JS Error: {error.get('text', 'Unknown')}")

        return result.get("result", {}).get("value")

    async def get_runtime_properties(self, object_id: str) -> List[Dict[str, Any]]:
        """
        Get properties of a runtime object

        Args:
            object_id: Object ID from Runtime

        Returns:
            List of properties
        """
        result = await self.send_command("Runtime.getProperties", {
            "objectId": object_id
        })
        return result.get("result", [])

    # Page Commands

    async def get_page_dimensions(self) -> Dict[str, int]:
        """
        Get viewport and page dimensions

        Returns:
            Dictionary with width, height, etc.
        """
        # Use JavaScript to get accurate dimensions
        width = await self.evaluate_js("window.innerWidth")
        height = await self.evaluate_js("window.innerHeight")
        scroll_x = await self.evaluate_js("window.scrollX")
        scroll_y = await self.evaluate_js("window.scrollY")

        return {
            "width": width,
            "height": height,
            "scrollX": scroll_x,
            "scrollY": scroll_y
        }

    async def take_screenshot(self) -> Optional[bytes]:
        """
        Take screenshot of current page

        Returns:
            Screenshot data or None
        """
        try:
            result = await self.send_command("Page.captureScreenshot", {
                "format": "png",
                "quality": 80,
                "fromSurface": True
            })
            data = result.get("data")
            if data:
                import base64
                return base64.b64decode(data)
            return None
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    async def capture_screenshot(self, output_path: str) -> bool:
        """
        Capture screenshot and save to file

        Args:
            output_path: Path to save screenshot

        Returns:
            True if successful
        """
        try:
            screenshot_data = await self.take_screenshot()
            if screenshot_data:
                with open(output_path, 'wb') as f:
                    f.write(screenshot_data)
                logger.info(f"Screenshot saved: {output_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False

    # Network Commands

    async def clear_browser_cache(self) -> bool:
        """Clear browser cache"""
        try:
            await self.send_command("Network.clearBrowserCache")
            return True
        except Exception as e:
            logger.error(f"Clear cache failed: {e}")
            return False

    # Helper methods

    async def reload_page(self) -> bool:
        """Reload current page"""
        try:
            await self.send_command("Page.reload")
            return True
        except Exception as e:
            logger.error(f"Reload failed: {e}")
            return False

    async def navigate_to(self, url: str) -> bool:
        """
        Navigate to URL

        Args:
            url: URL to navigate to

        Returns:
            True if successful
        """
        try:
            await self.send_command("Page.navigate", {"url": url})
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False

    async def is_connected(self) -> bool:
        """Check if still connected to Chrome"""
        if not self.ws or not self._running:
            return False

        try:
            # Test with simple command
            await asyncio.wait_for(
                self.send_command("Runtime.getVersion"),
                timeout=1.0
            )
            return True
        except:
            return False

    def __repr__(self) -> str:
        connected = "connected" if self.ws and self._running else "disconnected"
        return f"ChromeDevToolsManager({self.ws_url}, {connected})"
