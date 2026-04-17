FROM node:22-slim

WORKDIR /app

# Node dependencies (production only)
COPY webapp/package*.json ./webapp/
RUN cd webapp && npm ci --omit=dev

# Pre-built frontend (built locally with VITE_DOCKER_MODE=true before deploy)
COPY webapp/dist    ./webapp/dist
COPY webapp/server  ./webapp/server
COPY webapp/server.js ./webapp/server.js

# Data — pre-generated JSON + gold/predictions for Samples and Lookup tabs
COPY data/cross_dataset_performance.json ./data/cross_dataset_performance.json
COPY data/label_statistics.json          ./data/label_statistics.json
COPY data/relation_signatures.json       ./data/relation_signatures.json
COPY data/reproduce_results.json         ./data/reproduce_results.json
COPY data/reported_performance.json      ./data/reported_performance.json
COPY data/example_papers.json            ./data/example_papers.json
COPY data/webapp_metadata.json           ./data/webapp_metadata.json
COPY data/allowed_signatures.yaml        ./data/allowed_signatures.yaml
COPY data/gold                           ./data/gold
COPY data/predictions_v6                 ./data/predictions_v6
COPY data/annotation_lookup             ./data/annotation_lookup

# Reports (sidebar markdown) and schema configs
COPY reports ./reports
COPY configs  ./configs

EXPOSE 7860

CMD ["node", "webapp/server.js"]
