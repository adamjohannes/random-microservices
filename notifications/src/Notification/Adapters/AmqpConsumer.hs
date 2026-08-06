module Notification.Adapters.AmqpConsumer (startConsuming) where

import Control.Monad (forM_)
import Data.Aeson (eitherDecodeStrict)
import qualified Data.ByteString.Lazy as BL
import qualified Data.Text as T
import Network.AMQP
import Notification.Config (AmqpConfig (..))
import Notification.Domain.Event (EventPayload)

exchangeName :: T.Text
exchangeName = "domain_events"

queueBindings :: [(T.Text, T.Text)]
queueBindings =
  [ ("notifications.account.user_registered",      "account.user_registered")
  , ("notifications.course.user_enrolled",         "course.user_enrolled")
  , ("notifications.connections.request_received", "connections.request_received")
  , ("notifications.connections.request_accepted", "connections.request_accepted")
  ]

startConsuming :: AmqpConfig -> (EventPayload -> IO ()) -> IO Connection
startConsuming cfg handler = do
  conn <- openConnection (amqpHost cfg) "/" (T.unpack $ amqpUser cfg) (T.unpack $ amqpPass cfg)
  chan <- openChannel conn

  declareExchange chan newExchange
    { exchangeName    = exchangeName
    , exchangeType    = "topic"
    , exchangeDurable = True
    }

  forM_ queueBindings $ \(qName, routingKey) -> do
    _ <- declareQueue chan newQueue
      { queueName    = qName
      , queueDurable = True
      }
    bindQueue chan qName exchangeName routingKey
    _ <- consumeMsgs chan qName Ack $ \(msg, env) -> do
      let body = BL.toStrict (msgBody msg)
      case eitherDecodeStrict body of
        Left err  -> putStrLn $ "decode error on " <> T.unpack qName <> ": " <> err
        Right evt -> handler evt
      ackEnv env
    pure ()

  pure conn
