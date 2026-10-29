#!/usr/bin/env sh
set -eu

PROFILE="${1:-ci-all-strategies}"
IMAGE="${GUARDRAILS_LAB_IMAGE:-guardrails-strategies:local}"

mkdir -p reports
docker build -t "${IMAGE}" .

if [ "${PROFILE}" = "ci-guardrails-eval" ]; then
  CMD="evaluate-pipeline"
else
  CMD="measure"
fi

docker run --rm -v "$(pwd)/reports:/reports" "${IMAGE}" \
  "${CMD}" --profile "${PROFILE}" --output "/reports/measure-${PROFILE}.json"

docker run --rm -v "$(pwd)/reports:/reports" "${IMAGE}" \
  check-measure --profile "${PROFILE}" --report "/reports/measure-${PROFILE}.json"

echo "Measure profile ${PROFILE} passed. Report: reports/measure-${PROFILE}.json"
