"""
Manual WebSocket test client for testing the WebSocket functionality

This script connects to the WebSocket endpoint and allows for manual testing
of the WebSocket functionality. It connects to the server and sends/receives
messages to verify connection and message handling.

Usage:
    python manual_websocket_test.py [--host HOST] [--port PORT]
"""

import asyncio
import json
import argparse
import websockets
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def connect_and_test(host, port):
    """Connect to the WebSocket server and run tests"""
    uri = f"ws://{host}:{port}/ws"
    
    logger.info(f"Connecting to {uri}...")
    test_results = {}
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connection established!")
            test_results["connection"] = "SUCCESS"
            
            # Test 1: Ping/Pong
            logger.info("\n==== TEST 1: Ping/Pong ====")
            await send_message(websocket, {"type": "ping"})
            
            try:
                response = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if response.get("type") == "pong":
                    logger.info("✅ PING/PONG TEST PASSED")
                    test_results["ping_pong"] = "SUCCESS"
                else:
                    logger.error(f"❌ PING/PONG TEST FAILED: Expected 'pong' response, got {response}")
                    test_results["ping_pong"] = "FAILED"
            except asyncio.TimeoutError:
                logger.error("❌ PING/PONG TEST FAILED: Timeout waiting for response")
                test_results["ping_pong"] = "TIMEOUT"
            
            # Test 2: Instruction Processing
            logger.info("\n==== TEST 2: Instruction Processing ====")
            await send_message(websocket, {
                "type": "instruction",
                "instruction": "Create a simple test scene",
                "context": {}
            })
            
            try:
                # Should get acknowledgment
                ack = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if ack.get("type") != "ack":
                    logger.warning(f"Expected 'ack' message, got {ack}")
                
                # Should get status update
                status = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if status.get("type") != "status":
                    logger.warning(f"Expected 'status' message, got {status}")
                
                # Should get result
                result = await asyncio.wait_for(receive_message(websocket), timeout=10)
                if result.get("type") == "result":
                    logger.info("✅ INSTRUCTION TEST PASSED")
                    test_results["instruction"] = "SUCCESS"
                else:
                    logger.error(f"❌ INSTRUCTION TEST FAILED: Expected 'result' response, got {result}")
                    test_results["instruction"] = "FAILED"
            except asyncio.TimeoutError:
                logger.error("❌ INSTRUCTION TEST FAILED: Timeout waiting for response")
                test_results["instruction"] = "TIMEOUT"
            
            # Test 3: Tool Execution
            logger.info("\n==== TEST 3: Tool Execution ====")
            await send_message(websocket, {
                "type": "tool",
                "tool_name": "scene_generator",
                "parameters": {
                    "description": "A simple scene with a cube"
                }
            })
            
            try:
                # Should get acknowledgment
                ack = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if ack.get("type") != "ack":
                    logger.warning(f"Expected 'ack' message, got {ack}")
                
                # Should get status update
                status = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if status.get("type") != "status":
                    logger.warning(f"Expected 'status' message, got {status}")
                
                # Should get result
                result = await asyncio.wait_for(receive_message(websocket), timeout=10)
                if result.get("type") == "result":
                    logger.info("✅ TOOL EXECUTION TEST PASSED")
                    test_results["tool_execution"] = "SUCCESS"
                else:
                    logger.error(f"❌ TOOL EXECUTION TEST FAILED: Expected 'result' response, got {result}")
                    test_results["tool_execution"] = "FAILED"
            except asyncio.TimeoutError:
                logger.error("❌ TOOL EXECUTION TEST FAILED: Timeout waiting for response")
                test_results["tool_execution"] = "TIMEOUT"
            
            # Test 4: Error Handling
            logger.info("\n==== TEST 4: Error Handling ====")
            await send_message(websocket, {
                "type": "unknown_command",
                "data": "This should trigger an error response"
            })
            
            try:
                response = await asyncio.wait_for(receive_message(websocket), timeout=5)
                if response.get("type") == "error":
                    logger.info("✅ ERROR HANDLING TEST PASSED")
                    test_results["error_handling"] = "SUCCESS"
                else:
                    logger.error(f"❌ ERROR HANDLING TEST FAILED: Expected 'error' response, got {response}")
                    test_results["error_handling"] = "FAILED"
            except asyncio.TimeoutError:
                logger.error("❌ ERROR HANDLING TEST FAILED: Timeout waiting for response")
                test_results["error_handling"] = "TIMEOUT"
                
            logger.info("\n==== TEST SUMMARY ====")
            all_passed = True
            for test, result in test_results.items():
                status_symbol = "✅" if result == "SUCCESS" else "❌"
                logger.info(f"{status_symbol} {test}: {result}")
                if result != "SUCCESS":
                    all_passed = False
            
            if all_passed:
                logger.info("\n🎉 ALL TESTS PASSED!")
            else:
                logger.error("\n❌ SOME TESTS FAILED - See details above")
                
            return all_passed
    
    except Exception as e:
        logger.error(f"Error connecting to WebSocket server: {str(e)}")
        return False
    
    return True

async def send_message(websocket, message):
    """Send a message to the WebSocket server"""
    message_str = json.dumps(message)
    logger.info(f"Sending: {message_str}")
    await websocket.send(message_str)

async def receive_message(websocket):
    """Receive a message from the WebSocket server"""
    message = await websocket.recv()
    try:
        parsed = json.loads(message)
        logger.info(f"Received: {json.dumps(parsed, indent=2)}")
        return parsed
    except json.JSONDecodeError:
        logger.warning(f"Received non-JSON message: {message}")
        return message

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Manual WebSocket test client')
    parser.add_argument('--host', default='localhost', help='WebSocket server host')
    parser.add_argument('--port', type=int, default=8000, help='WebSocket server port')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds for waiting for responses')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show test results, not detailed messages')
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Print a nice header
    print("\n" + "=" * 70)
    print(f"{'WebSocket Connection Test':^70}")
    print(f"{'GenAI Agent 3D':^70}")
    print("=" * 70)
    
    logger.info(f"Starting WebSocket test client for {args.host}:{args.port}")
    
    # Check if server is running
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((args.host, args.port))
        sock.close()
        if result != 0:
            logger.error(f"\n❌ ERROR: Server not running on {args.host}:{args.port}")
            logger.error(f"Please start the server with: python run_server.py --test-mode --port {args.port}")
            exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR checking server: {str(e)}")
        exit(1)
    
    try:
        success = asyncio.run(connect_and_test(args.host, args.port))
        
        if success:
            print("\n" + "=" * 70)
            print(f"{'🎉 ALL TESTS PASSED! 🎉':^70}")
            print("=" * 70 + "\n")
            exit(0)
        else:
            print("\n" + "=" * 70)
            print(f"{'❌ SOME TESTS FAILED ❌':^70}")
            print("=" * 70 + "\n")
            exit(1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        logger.error(f"\n❌ Unexpected error during testing: {str(e)}")
        exit(2)

if __name__ == "__main__":
    main()
