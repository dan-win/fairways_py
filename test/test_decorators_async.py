import unittest


import json
import os


def setUpModule():
    pass

def tearDownModule():
    pass


class IoTaskTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import asyncio
        from fairways.decorators import asyncmethod
        import time
        import concurrent.futures
        import re
        cls.asyncio = asyncio
        cls.asyncmethod = asyncmethod
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re
        # import os
        # cls.os = os

    @classmethod
    def tearDownClass(cls):
        pass

    def test_io_task_order_and_result(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio

        trace = asyncio.Queue()

        def syn1(data):
            return data + [1]

        @asyncmethod.io_task
        async def asyn2(data):
            await asyncio.sleep(1)
            return data + [2]

        def syn3(data):
            return data + [3]

        data = []

        data = syn1(data)
        data = asyn2(data)
        data = syn3(data)

        self.assertListEqual(data, [1, 2, 3])

    @unittest.skip("Refactor this example, its totally wrong (asyncio.Queue is not thread safe, there are no running loops in threads by default!)")
    def test_io_task_concurrent(self):
        """
        """

        asyncmethod = self.asyncmethod
        asyncio = self.asyncio
        futures = self.futures
        re = self.re

        FIRST = "1"
        SECOND = "2"

        jumps_to_second = re.compile(f'{FIRST}{SECOND}')
        jumps_to_first = re.compile(f'{SECOND}{FIRST}')

        trace = asyncio.Queue()

        def thread1(queue):

            def syn1(q):
                return q.put_nowait(FIRST)

            @asyncmethod.io_task
            async def asyn2(q):
                await asyncio.sleep(1)
                return await q.put(FIRST)

            def syn3(q):
                return q.put_nowait(FIRST)

            syn1(queue)
            asyn2(queue)
            syn3(queue)

        def thread2(queue):

            def syn1(q):
                return q.put_nowait(SECOND)

            @asyncmethod.io_task
            async def asyn2(q):
                await asyncio.sleep(1)
                return await q.put(SECOND)

            def syn3(q):
                return q.put_nowait(SECOND)

            syn1(queue)
            asyn2(queue)
            syn3(queue)

        futures_list = []

        with futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures_list.append(executor.submit(thread1, trace))
            futures_list.append(executor.submit(thread2, trace))


        for future in futures.as_completed(futures_list):
            try:
                data = future.result()
            except Exception as exc:
                print(f'generated an exception: {exc}')
            else:
                print('future ok')

        # completed, uncompleted = futures.wait(futures_list)        
        # print(f"-----------------> completed: {completed}, uncompleted: {uncompleted}")

        steps = []
        while not trace.empty():
            steps.append(trace.get_nowait())
        
        line = "".join(steps)

        steps_count = len(line)
        self.assertEqual(steps_count, 6, "Some steps were not executed")
        self.assertTrue(jumps_to_second.search(line) is not None, "No transitions to second thread")
        self.assertTrue(jumps_to_first.search(line) is not None, "No transitions to first thread")

    def test_io_task_returns_value(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio

        @asyncmethod.io_task
        async def asyn2(data):
            await asyncio.sleep(1)
            return data
        
        result = asyn2("VALUE")
        
        self.assertEqual(result, "VALUE")

    def test_io_task_raises_error(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio

        trace = asyncio.Queue()

        @asyncmethod.io_task
        async def asyn2():
            1/0
            await asyncio.sleep(1)
        
        with self.assertRaises(ZeroDivisionError, msg="Exception was lost!"):
            asyn2()


class CpuTaskTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import asyncio
        from fairways.decorators import asyncmethod
        import time
        import concurrent.futures
        import re
        cls.asyncio = asyncio
        cls.asyncmethod = asyncmethod
        cls.time = time
        cls.futures = concurrent.futures
        cls.re = re
        # import os
        # cls.os = os

    @classmethod
    def tearDownClass(cls):
        pass

    def test_cpu_task_order_and_result(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio
        time = self.time 

        trace = asyncio.Queue()

        def syn1(data):
            return data + [1]

        @asyncmethod.cpu_task
        def heavy_syn(data):
            time.sleep(1)
            return data + [2]

        def syn3(data):
            return data + [3]

        data = []

        data = syn1(data)
        data = heavy_syn(data)
        data = syn3(data)

        self.assertListEqual(data, [1, 2, 3])

    def test_cpu_task_returns_value(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio
        time = self.time

        @asyncmethod.cpu_task
        def heavy_syn(data):
            time.sleep(1)
            return data
        
        result = heavy_syn("VALUE")
        
        self.assertEqual(result, "VALUE")

    def test_cpu_task_raises_error(self):
        """
        """
        asyncmethod = self.asyncmethod
        asyncio = self.asyncio
        time = self.time

        trace = asyncio.Queue()

        @asyncmethod.cpu_task
        def heavy_syn():
            1/0
            time.sleep(1)
        
        with self.assertRaises(ZeroDivisionError, msg="Exception was lost!"):
            heavy_syn()

    def test_cpu_task_concurrent(self):
        """
        """

        asyncmethod = self.asyncmethod
        asyncio = self.asyncio
        futures = self.futures
        time = self.time
        re = self.re

        FIRST = "1"
        SECOND = "2"

        jumps_to_second = re.compile(f'{FIRST}{SECOND}')
        jumps_to_first = re.compile(f'{SECOND}{FIRST}')

        trace = asyncio.Queue()

        def thread1(queue):

            def syn1(q):
                return q.put_nowait(FIRST)

            @asyncmethod.cpu_task
            def heavy_syn(q):
                time.sleep(1)
                q.put_nowait(FIRST)

            def syn3(q):
                return q.put_nowait(FIRST)

            syn1(queue)
            heavy_syn(queue)
            syn3(queue)

        def thread2(queue):

            def syn1(q):
                return q.put_nowait(SECOND)

            @asyncmethod.cpu_task
            def heavy_syn(q):
                time.sleep(1)
                q.put_nowait(SECOND)

            def syn3(q):
                return q.put_nowait(SECOND)

            syn1(queue)
            heavy_syn(queue)
            syn3(queue)

        futures_list = []

        with futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures_list.append(executor.submit(thread1, trace))
            futures_list.append(executor.submit(thread2, trace))

        for future in futures.as_completed(futures_list):
            try:
                data = future.result()
            except Exception as exc:
                print(f'generated an exception: {exc}')
            else:
                print('future ok')

        # completed, uncompleted = futures.wait(futures_list)        
        # print(f"-----------------> completed: {completed}, uncompleted: {uncompleted}")

        steps = []
        while not trace.empty():
            steps.append(trace.get_nowait())
        
        line = "".join(steps)

        steps_count = len(line)
        self.assertEqual(steps_count, 6, "Some steps were not executed")
        self.assertTrue(jumps_to_second.search(line) is not None, "No transitions to second thread")
        self.assertTrue(jumps_to_first.search(line) is not None, "No transitions to first thread")

