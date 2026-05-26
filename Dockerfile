FROM node:22-slim

WORKDIR /app

# Node dependencies (production only)
COPY webapp/package*.json ./webapp/
RUN cd webapp && npm ci --omit=dev

# Pre-built frontend (built locally with VITE_DOCKER_MODE=true before deploy)
COPY webapp/dist    ./webapp/dist
COPY webapp/server  ./webapp/server
COPY webapp/server.js ./webapp/server.js

# Data — pre-generated JSON/YAML served by API handlers
COPY data/webapp/cross_dataset_performance.json ./data/webapp/cross_dataset_performance.json
COPY data/webapp/label_statistics.json          ./data/webapp/label_statistics.json
COPY data/webapp/relation_signatures.json       ./data/webapp/relation_signatures.json
COPY data/webapp/reproduce_results.json         ./data/webapp/reproduce_results.json
COPY data/webapp/multi_sciere_results.json      ./data/webapp/multi_sciere_results.json
COPY data/webapp/example_papers.json            ./data/webapp/example_papers.json
COPY data/webapp/domain_shift_results.json      ./data/webapp/domain_shift_results.json
COPY data/webapp/semantic_groups.json           ./data/webapp/semantic_groups.json
COPY data/webapp/allowed_signatures.yaml        ./data/webapp/allowed_signatures.yaml
COPY data/webapp/static                         ./data/webapp/static
COPY data/webapp/confusion_matrices             ./data/webapp/confusion_matrices
COPY data/webapp/publication_map                ./data/webapp/publication_map

# Gold + annotation_lookup for Samples/Lookup tabs
COPY data/gold                           ./data/gold
COPY data/annotation_lookup             ./data/annotation_lookup

# Reports (sidebar markdown) and schema configs
COPY reports ./reports
COPY configs  ./configs

EXPOSE 7860

CMD ["node", "webapp/server.js"]
