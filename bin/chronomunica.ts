import { runAppStatic } from '..';

process.on('uncaughtExceptionMonitor', (err, origin) => {
  console.error(`Uncaught error from ${origin}: ${err.message}`);
});

runAppStatic();
