import requests
import json
import time
import logging
from typing import Optional, Dict, Any
from app.core.config import settings
from app.models.schemas import GitRollScan, GitRollScanResponse
import re

# Setup logging
logger = logging.getLogger(__name__)

class GitRollService:
    def __init__(self):
        self.api_url = settings.gitroll_api_url
        
    async def initiate_scan(self, username: str) -> GitRollScanResponse:
        """
        Initiate a GitRoll scan for a GitHub user
        """
        try:
            logger.info(f"Initiating GitRoll scan for user: {username}")
            payload = {"user": username}
            response = requests.post(self.api_url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                scan_id = data.get("scan_id") or self._extract_scan_id_from_response(data)
                user_id = data.get("user_id") or username  # Return username as user_id if not provided
                profile_url = f"https://gitroll.io/profile/{scan_id}" if scan_id else None
                
                logger.info(f"GitRoll scan initiated successfully for {username} - Scan ID: {scan_id}")
                
                return GitRollScanResponse(
                    success=True,
                    scan_id=scan_id,
                    profile_url=profile_url,
                    message="Scan initiated successfully",
                    user_id=user_id
                )
            else:
                logger.error(f"GitRoll scan initiation failed for {username}: {response.status_code} - {response.text}")
                return GitRollScanResponse(
                    success=False,
                    message=f"Failed to initiate scan: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Error initiating GitRoll scan for {username}: {str(e)}")
            return GitRollScanResponse(
                success=False,
                message=f"Error initiating scan: {str(e)}"
            )
    
    async def check_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Check the status of a GitRoll scan
        """
        try:
            logger.info(f"Checking GitRoll scan status for scan ID: {scan_id}")
            profile_url = f"https://gitroll.io/profile/{scan_id}"
            response = requests.get(profile_url)
            
            if response.status_code == 200:
                # Parse the HTML to extract score and OG image score
                score, og_image_score = self._parse_profile_page(response.text)
                
                status = "completed" if score is not None else "processing"
                logger.info(f"GitRoll scan {scan_id} status: {status}, score: {score}")
                
                return {
                    "success": True,
                    "scan_id": scan_id,
                    "profile_url": profile_url,
                    "score": score,
                    "og_image_score": og_image_score,
                    "status": status
                }
            else:
                logger.warning(f"GitRoll scan status check failed for {scan_id}: {response.status_code}")
                return {
                    "success": False,
                    "message": f"Failed to check scan status: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error checking GitRoll scan status for {scan_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error checking scan status: {str(e)}"
            }
    
    def _extract_scan_id_from_response(self, response_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract scan ID from GitRoll API response
        """
        # This is a placeholder - adjust based on actual API response format
        if isinstance(response_data, dict):
            return response_data.get("scan_id") or response_data.get("id")
        return None
    
    def _parse_profile_page(self, html_content: str) -> tuple[Optional[float], Optional[float]]:
        """
        Parse GitRoll profile page to extract scores
        """
        try:
            # Extract score from HTML - adjust selectors based on actual page structure
            score_match = re.search(r'"score":\s*([\d.]+)', html_content)
            og_image_score_match = re.search(r'"ogImageScore":\s*([\d.]+)', html_content)
            
            score = float(score_match.group(1)) if score_match else None
            og_image_score = float(og_image_score_match.group(1)) if og_image_score_match else None
            
            return score, og_image_score
            
        except Exception:
            return None, None
    
    async def wait_for_scan_completion(self, scan_id: str, max_wait_time: int = 300) -> Dict[str, Any]:
        """
        Wait for scan completion with timeout
        """
        start_time = time.time()
        logger.info(f"Waiting for GitRoll scan completion: {scan_id} (max wait: {max_wait_time}s)")
        
        while time.time() - start_time < max_wait_time:
            status = await self.check_scan_status(scan_id)
            
            if status.get("status") == "completed":
                elapsed_time = time.time() - start_time
                logger.info(f"GitRoll scan {scan_id} completed in {elapsed_time:.1f}s")
                return status
            
            # Wait 10 seconds before checking again
            elapsed = time.time() - start_time
            logger.info(f"GitRoll scan {scan_id} still processing... (elapsed: {elapsed:.1f}s)")
            time.sleep(10)
        
        logger.warning(f"GitRoll scan {scan_id} timed out after {max_wait_time}s")
        return {
            "success": False,
            "message": "Scan timeout - scan may still be processing"
        } 