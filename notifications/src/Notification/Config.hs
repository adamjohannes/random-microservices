module Notification.Config
  ( AppConfig (..)
  , AmqpConfig (..)
  , SmtpConfig (..)
  , loadConfig
  ) where

import Data.Maybe (fromMaybe)
import System.Environment (lookupEnv)
import System.Exit (die)
import qualified Data.Text as T

data AmqpConfig = AmqpConfig
  { amqpHost :: String
  , amqpUser :: T.Text
  , amqpPass :: T.Text
  }

data SmtpConfig = SmtpConfig
  { smtpHost     :: String
  , smtpPort     :: Int
  , smtpUser     :: T.Text
  , smtpPass     :: T.Text
  , smtpFromAddr :: T.Text
  , smtpFromName :: T.Text
  }

data AppConfig = AppConfig
  { appAmqp         :: AmqpConfig
  , appSmtp         :: SmtpConfig
  , appPort         :: Int
  , appAmqpDelaySecs :: Int
  }

loadConfig :: IO AppConfig
loadConfig = do
  amqpHost_ <- fromMaybe "localhost" <$> lookupEnv "AMQP_HOST"
  amqpUser_ <- T.pack . fromMaybe "guest" <$> lookupEnv "AMQP_USER"
  amqpPass_ <- T.pack . fromMaybe "guest" <$> lookupEnv "AMQP_PASS"

  smtpHost_ <- require "SMTP_HOST"
  smtpPort_ <- read . fromMaybe "587" <$> lookupEnv "SMTP_PORT"
  smtpUser_ <- T.pack <$> require "SMTP_USER"
  smtpPass_ <- T.pack <$> require "SMTP_PASS"
  smtpFrom_ <- T.pack <$> require "SMTP_FROM_ADDRESS"
  smtpName_ <- T.pack . fromMaybe "Platform Notifications" <$> lookupEnv "SMTP_FROM_NAME"

  port_     <- read . fromMaybe "8083" <$> lookupEnv "PORT"
  delay_    <- read . fromMaybe "0"    <$> lookupEnv "AMQP_STARTUP_DELAY_SECS"

  pure AppConfig
    { appAmqp          = AmqpConfig amqpHost_ amqpUser_ amqpPass_
    , appSmtp          = SmtpConfig smtpHost_ smtpPort_ smtpUser_ smtpPass_ smtpFrom_ smtpName_
    , appPort          = port_
    , appAmqpDelaySecs = delay_
    }

require :: String -> IO String
require key = lookupEnv key >>= \case
  Just v  -> pure v
  Nothing -> die $ "FATAL: required environment variable not set: " <> key
