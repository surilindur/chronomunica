FROM node:current-alpine AS build

WORKDIR /opt/chronomunica

COPY . .

RUN yarn install --frozen-lockfile --ignore-engines

FROM node:current-alpine

WORKDIR /opt/chronomunica

COPY --from=build /opt/chronomunica/package.json ./package.json
COPY --from=build /opt/chronomunica/packages ./packages
COPY --from=build /opt/chronomunica/engines ./engines
COPY --from=build /opt/chronomunica/node_modules ./node_modules

ENTRYPOINT [ "node", "engines/runner/bin/chronomunica.js" ]

ENV NODE_ENV production
