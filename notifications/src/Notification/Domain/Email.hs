module Notification.Domain.Email (EmailMessage (..)) where

import Data.Text (Text)

data EmailMessage = EmailMessage
  { emTo      :: Text
  , emSubject :: Text
  , emBody    :: Text
  } deriving (Show, Eq)
