import parcing_woman
import parcing
import schedule
import time



def main():
    # schedule.every().day.at('11:17').do(make_mans_db)
    # schedule.every().day.at('19:00').do(make_mans_db)
    # schedule.every().day.at('11:18').do(make_woman_db)
    # schedule.every().day.at('19:01').do(make_woman_db)
    parcing_woman.make_woman_db()
    parcing_woman.clear_derectory_data_g()
    time.sleep(4)
    parcing.make_mans_db()
    parcing.clear_derectory_data()


    # while True:
    #     schedule.run_pending()

if __name__ == '__main__':
    main()
