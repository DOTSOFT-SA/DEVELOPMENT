"""
/*
 * Copyright 2025 DOTSOFT SA, Inc All Rights Reserved.
 *
 * Author: Georgios Karanasios R&D Software Engineer
 */
"""

import asyncio

import schedule

from prediction import main as prediction_main


def schedule_job():
    print("\n🚀 Running scheduled task: Calling main() from prediction.py")
    asyncio.create_task(prediction_main())


async def main():

    # Run the job immediately before starting the schedule
    print("\n Initial execution of `prediction_main()` started... \n")
    await prediction_main()
    print("\n✅ Initial execution of `prediction_main()` completed. Schedule starts...\n")

    print("📅 Scheduler started. Running every Sunday at 00:00...")
    schedule.every().sunday.at("00:00").do(schedule_job)
    while True:
        schedule.run_pending()  # Checks if it’s time to run
        await asyncio.sleep(10)  # Wait 10 seconds before checking to run again


if __name__ == "__main__":
    asyncio.run(main())
