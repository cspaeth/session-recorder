FROM node:12

#RUN apt-get update -y
#RUN apt-get install -y inotify-tools

ENV YARN_VERSION 1.22.4

RUN curl -fSLO --compressed "https://yarnpkg.com/downloads/$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz" \
    && tar -xzf yarn-v$YARN_VERSION.tar.gz -C /opt/ \
    && ln -snf /opt/yarn-v$YARN_VERSION/bin/yarn /usr/local/bin/yarn \
    && ln -snf /opt/yarn-v$YARN_VERSION/bin/yarnpkg /usr/local/bin/yarnpkg \
    && rm yarn-v$YARN_VERSION.tar.gz

RUN yarn global add @quasar/cli

RUN mkdir /src
WORKDIR /src


COPY package.json .
COPY yarn.lock .

RUN yarn install
#CMD tail -f /dev/null
CMD quasar dev
