from flask import Flask, jsonify, request
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_app")

# Tracing
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
tracer = trace.get_tracer(__name__)

# Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint"])

# Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def home():
    logger.info("Home endpoint hit")
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    return jsonify({"message": "Welcome to Observability!"})

@app.route("/hello")
def hello():
    logger.info("Hello endpoint hit")
    REQUEST_COUNT.labels(method="GET", endpoint="/hello").inc()
    return jsonify({"message": "Hello, world!"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
