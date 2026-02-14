import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.scraper import SiriusScraper
from src.utils import setup_logging

logger = setup_logging()

def diagnose():
    logger.info("Starting dashboard diagnosis...")
    
    scraper = SiriusScraper(headless=False)
    scraper.start()
    
    try:
        if scraper.login():
            logger.info("Login successful. Waiting for dashboard to load...")
            time.sleep(10)  # Give it plenty of time to fully load
            
            # Save main dashboard screenshot
            scraper.driver.save_screenshot("dashboard_diagnostic.png")
            logger.info("Saved dashboard_diagnostic.png")
            
            # Save main dashboard HTML
            with open("dashboard_dump.html", "w", encoding="utf-8") as f:
                f.write(scraper.driver.page_source)
            logger.info("Saved dashboard_dump.html")
            
            # Try to identify frames
            frames = scraper.driver.find_elements(By.TAG_NAME, "frame")
            logger.info(f"Found {len(frames)} frames on the main page.")
            
            for index, frame in enumerate(frames):
                frame_name = frame.get_attribute("name")
                frame_id = frame.get_attribute("id")
                logger.info(f"Frame {index}: Name='{frame_name}', ID='{frame_id}'")
                
                # Switch to frame and dump content
                try:
                    scraper.driver.switch_to.frame(frame)
                    time.sleep(1)
                    with open(f"frame_{frame_name or index}_dump.html", "w", encoding="utf-8") as f:
                        f.write(scraper.driver.page_source)
                    logger.info(f"Saved dump for frame '{frame_name or index}'")
                    scraper.driver.switch_to.default_content()
                except Exception as e:
                    logger.error(f"Error dumping frame {frame_name}: {e}")
                    scraper.driver.switch_to.default_content()

            logger.info("Diagnosis complete. Please check the generated .html and .png files.")
            
        else:
            logger.error("Login failed.")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        scraper.quit()

if __name__ == "__main__":
    diagnose()
