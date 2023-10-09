FROM node:current-alpine AS build

WORKDIR /opt/chronomunica

COPY . .

RUN corepack enable && yarn install --immutable && yarn build

FROM python:3-alpine

WORKDIR /opt/chronomunica

COPY --from=build /opt/chronomunica/runner ./runner
COPY --from=build /opt/chronomunica/tool ./tool
COPY --from=build /opt/chronomunica/package.json ./package.json
COPY --from=build /opt/chronomunica/node_modules ./node_modules
COPY --from=build /opt/chronomunica/requirements.txt ./requirements.txt

RUN python -m pip install -r requirements.txt

ENTRYPOINT [ "python", "tool/chronomunica.py" ]
