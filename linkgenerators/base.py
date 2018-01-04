from threading import Thread

class Scrapper(Thread):
    def __init__(self, queue, timeout=10):
        Thread.__init__(self)
        self.name = 'Base'
        self.queue = queue
        self.timeout = timeout

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.join()

    def run(self):
        try:
            self.queue.put(self.get_link())
        except Exception as e:
            print("Scrapper %s Failed %s" % (self.name, e))

    def get_link(self):
        raise NotImplementedError
