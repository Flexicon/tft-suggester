## TFT Suggester Backend

### Dev

To prepare the dev env on macOS, run the following in your terminal:

```
$ make dev && source ./venv/bin/activate
```

_Note: Docker cli with Compose is required for the above make script_

To run the api server:

```
$ uvicorn api:app --host=0.0.0.0 --reload
```

To run the web scrapers:

```
$ python -m scraper
```
