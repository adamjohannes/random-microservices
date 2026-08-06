module Notification.Health
  ( HealthAPI
  , healthServer
  , HealthResponse (..)
  ) where

import Data.Aeson (ToJSON)
import GHC.Generics (Generic)
import Servant

data HealthResponse = HealthResponse { status :: String }
  deriving (Show, Generic)

instance ToJSON HealthResponse

type HealthAPI = "health" :> Get '[JSON] HealthResponse

healthServer :: Server HealthAPI
healthServer = pure (HealthResponse "ok")
