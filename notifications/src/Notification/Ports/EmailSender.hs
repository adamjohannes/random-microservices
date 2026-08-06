module Notification.Ports.EmailSender (EmailSender (..)) where

import Notification.Domain.Email (EmailMessage)

class Monad m => EmailSender m where
  sendEmail :: EmailMessage -> m (Either String ())
