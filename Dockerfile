FROM node:current-alpine AS build

WORKDIR /opt/chronomunica

COPY . .

RUN corepack enable && corepack prepare yarn@stable --activate
RUN yarn install --immutable && yarn build

FROM gcr.io/distroless/nodejs20-debian11

WORKDIR /opt/chronomunica

COPY --from=build /opt/chronomunica/bin ./bin
COPY --from=build /opt/chronomunica/src ./src
COPY --from=build /opt/chronomunica/package.json ./package.json
COPY --from=build /opt/chronomunica/node_modules ./node_modules

CMD [ "bin/chronomunica.js" ]

ENV NODE_ENV production
