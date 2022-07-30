import script
import multiprocessing

if __name__ == "__main__":
    for i in range(4 * 8):
        p = multiprocessing.Process(target=script.main)
        p.start()
        p.join()
