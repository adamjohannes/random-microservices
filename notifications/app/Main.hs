module Main (main) where

import Control.Concurrent (forkIO, threadDelay)
import Control.Exception (SomeException, try)
import Control.Monad (forever)
import System.IO (hSetBuffering, stdout, stderr, BufferMode(..))
import Network.Wai.Handler.Warp (run)
import Servant (Proxy (..), serve)

import Notification.Adapters.AmqpConsumer (startConsuming)
import Notification.Adapters.SmtpEmail (runSmtpEmailM)
import Notification.Config (AppConfig, appAmqp, appPort, appSmtp, loadConfig)
import Notification.Domain.Dispatch (dispatch)
import Notification.Domain.Email (emTo)
import Notification.Health (HealthAPI, healthServer)
import Notification.Ports.EmailSender (sendEmail)

main :: IO ()
main = do
  hSetBuffering stdout LineBuffering
  hSetBuffering stderr LineBuffering
  cfg <- loadConfig
  _ <- forkIO $ connectWithRetry cfg 1
  let port = appPort cfg
  putStrLn $ "notifications service listening on port " <> show port
  run port (serve (Proxy :: Proxy HealthAPI) healthServer)

connectWithRetry :: AppConfig -> Int -> IO ()
connectWithRetry cfg attempt = do
  result <- try @SomeException $
    startConsuming (appAmqp cfg) $ \evt ->
      case dispatch evt of
        Nothing  -> putStrLn "no email mapped for event (ignoring)"
        Just msg -> do
          putStrLn $ "dispatching email to " <> show (emTo msg)
          r <- runSmtpEmailM (appSmtp cfg) (sendEmail msg)
          case r of
            Left err -> putStrLn $ "smtp error: " <> err
            Right _  -> putStrLn $ "email sent to " <> show (emTo msg)
  case result of
    Right _  -> pure ()
    Left err -> do
      let delaySecs = min (attempt * 5) 30
      putStrLn $ "AMQP connection failed (attempt " <> show attempt
               <> "), retrying in " <> show delaySecs <> "s: " <> show err
      threadDelay (delaySecs * 1_000_000)
      connectWithRetry cfg (attempt + 1)
