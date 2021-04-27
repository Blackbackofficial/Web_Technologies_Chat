import concurrent.futures
from datetime import datetime, timezone
from json import dumps
from timeit import timeit

from django.http import HttpResponse


_status_jobs = []


def ping(request):
    """Handler that simply returns `pong` from a GET.
    """
    return HttpResponse("pong")


def time(request):
    """Handler that returns server time, in both local/utc/epoch, along with the timezone
    """
    utc_time = datetime.now(timezone.utc)
    local_time = utc_time.astimezone()
    times = {
        "epoch": int(utc_time.timestamp()),
        "local": local_time.isoformat(),
        "offset": local_time.utcoffset().total_seconds()/60/60,
        "utc": utc_time.isoformat(),
        "zone": local_time.tzname()
    }
    return HttpResponse(dumps(times), content_type='application/json')


def status(request):
    """Handler that calls each status job in a worker pool, attempting to timeout.
    The resulting durations/errors are written to the response
    as JSON.

    eg.

    `{
        "endpoints": [
            { "endpoint": "Jenny's Database", "duration": 1.002556324005127 },
            { "endpoint": "Hotmail", "duration": -1, "error": "Host is down" },
        ]
     }`
    """
    endpoints = []
    stats = {"endpoints": None}

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    # This is basically calling the below within the executor:
    #
    #     >>> timeit(job[2], number=1)
    #
    # job is a tuple of (name, timeout, func) so the above is really:
    #     >>> timeit(func, number=1)
    #
    #gen = ((job, executor.submit(timeit, job[2], number=1)) for job in jobs)
    #for job, future in gen:
    for job, future in [(job, executor.submit(timeit, job[2], number=1)) for job in _status_jobs]:
        name, timeout, _ = job
        endpoint = {"endpoint": name}
        try:
            data = future.result(timeout=timeout)
            endpoint["duration"] = data
        except concurrent.futures.TimeoutError:
            endpoint["error"] = "timeout exceeded"
        except Exception as ex:
            endpoint["error"] = str(ex)
        endpoints.append(endpoint)

    if len(endpoints) > 0:
        stats["endpoints"] = endpoints

    executor.shutdown(wait=False)
    return HttpResponse(dumps(stats), content_type='application/json')
    # TODO: Look into potentially cleaning up jobs that have timed-out.
    #
    #       This could be done by changing jobs from a func to an object
    #       that implements `def interrupt(self):` which would be used
    #       to interrupt/stop/close/cleanup any resources.
