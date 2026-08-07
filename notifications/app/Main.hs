module Main (main) where

import Control.Concurrent (forkIO, threadDelay)
import Control.Exception (SomeException, try)
import Control.Monad (when)
import System.IO (BufferMode (..), hPutStrLn, hSetBuffering, stderr, stdout)
import Network.Wai.Handler.Warp (run)
import Servant (Proxy (..), serve)

import Notification.Adapters.AmqpConsumer (startConsuming)
import Notification.Adapters.SmtpEmail (runSmtpEmailM)
import Notification.Config (AppConfig, appAmqp, appAmqpDelaySecs, appPort, appSmtp, loadConfig)
import Notification.Domain.Dispatch (dispatch)
import Notification.Domain.Email (emTo)
import Notification.Health (HealthAPI, healthServer)
import Notification.Ports.EmailSender (sendEmail)

logS :: String -> IO ()
logS = hPutStrLn stderr

main :: IO ()
main = do
  hSetBuffering stdout LineBuffering
  hSetBuffering stderr LineBuffering
  cfg <- loadConfig
  let delay = appAmqpDelaySecs cfg
  when (delay > 0) $ do
    logS $ "waiting " <> show delay <> "s before connecting to AMQP"
    threadDelay (delay * 1_000_000)
  _ <- forkIO $ connectWithRetry cfg 1
  let port = appPort cfg
  logS $ "notifications service listening on port " <> show port
  run port (serve (Proxy :: Proxy HealthAPI) healthServer)

connectWithRetry :: AppConfig -> Int -> IO ()
connectWithRetry cfg attempt = do
  logS $ "AMQP: connecting to broker (attempt " <> show attempt <> ")"
  result <- try @SomeException $
    startConsuming (appAmqp cfg) $ \evt ->
      case dispatch evt of
        Nothing  -> logS "event received: no email mapped (ignoring)"
        Just msg -> do
          logS $ "event received: dispatching email to " <> show (emTo msg)
          r <- runSmtpEmailM (appSmtp cfg) (sendEmail msg)
          case r of
            Left err -> logS $ "smtp error: " <> err
            Right _  -> logS $ "email sent to " <> show (emTo msg)
  case result of
    Right _  -> pure ()
    Left err -> do
      let delaySecs = min (attempt * 5) 30
      logS $ "AMQP connection failed (attempt " <> show attempt
          <> "), retrying in " <> show delaySecs <> "s: " <> show err
      threadDelay (delaySecs * 1_000_000)
      connectWithRetry cfg (attempt + 1)
