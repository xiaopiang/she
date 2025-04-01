from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django.utils import timezone
import logging

from tickets.utils.scraper import scrape_movies

logger = logging.getLogger(__name__)

def start():
    """
    啟動背景排程器，定期執行爬蟲任務
    """
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # 每天凌晨2點執行爬蟲任務
    scheduler.add_job(
        scrape_movies,
        'cron',
        hour=2,
        minute=0,
        id='scrape_movies_job',
        replace_existing=True,
        name='更新電影資訊'
    )
    
    # 系統啟動時也執行一次爬蟲
    scheduler.add_job(
        scrape_movies,
        'date',
        run_date=timezone.now() + timezone.timedelta(seconds=10),
        id='initial_scrape_job',
        replace_existing=True,
        name='初始化電影資訊'
    )
    
    try:
        logger.info("啟動排程器...")
        scheduler.start()
    except Exception as e:
        logger.error(f"啟動排程器時發生錯誤: {str(e)}")
        scheduler.shutdown()