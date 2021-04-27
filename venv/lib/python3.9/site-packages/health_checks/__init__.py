from health_checks.views import _status_jobs


def add_status_job(job_func, name=None, timeout=3):
    """Adds a job to be included during calls to the `/status` endpoint.

    :param job_func: the status function.
    :param name: the name used in the JSON response for the given status
                    function. The name of the function is the default.
    :param timeout: the time limit before the job status is set to
                    "timeout exceeded".
    """
    job_name = job_func.__name__ if name is None else name
    job = (job_name, timeout, job_func)
    _status_jobs.append(job)


def status_job(fn=None, name=None, timeout=3):
    """Decorator that invokes `add_status_job`.

    ::

        @app.status_job
        def postgresql():
            # query/ping postgres

        @app.status_job(name="Active Directory")
        def active_directory():
            # query active directory

        @app.status_job(timeout=5)
        def paypal():
            # query paypal, timeout after 5 seconds

    """
    if fn is None:
        def decorator(fn):
            add_status_job(fn, name, timeout)
        return decorator
    else:
        add_status_job(fn, name, timeout)
