module Main (main) where

import Control.Concurrent (forkIO, threadDelay)
import Control.Monad (forever)
import Network.Wai.Handler.Warp (run)
import Servant (Proxy (..), serve)

import Notification.Adapters.AmqpConsumer (startConsuming)
import Notification.Adapters.SmtpEmail (runSmtpEmailM)
import Notification.Config (appAmqp, appPort, appSmtp, loadConfig)
import Notification.Domain.Dispatch (dispatch)
import Notification.Domain.Email (emTo)
import Notification.Health (HealthAPI, healthServer)
import Notification.Ports.EmailSender (sendEmail)

main :: IO ()
main = do
  cfg <- loadConfig

  _ <- forkIO $ do
    _ <- startConsuming (appAmqp cfg) $ \evt ->
      case dispatch evt of
        Nothing  -> putStrLn "no email mapped for event (ignoring)"
        Just msg -> do
          result <- runSmtpEmailM (appSmtp cfg) (sendEmail msg)
          case result of
            Left err -> putStrLn $ "smtp error: " <> err
            Right _  -> putStrLn $ "email sent to " <> show (emTo msg)
    forever $ threadDelay maxBound

  let port = appPort cfg
  putStrLn $ "notifications service listening on port " <> show port
  run port (serve (Proxy :: Proxy HealthAPI) healthServer)
