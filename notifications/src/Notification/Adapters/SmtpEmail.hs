module Notification.Adapters.SmtpEmail
  ( SmtpEmailM (..)
  , runSmtpEmailM
  ) where

import Control.Exception (SomeException, try)
import Control.Monad.IO.Class (liftIO)
import Control.Monad.Reader (ReaderT, ask, runReaderT)
import qualified Data.Text.Lazy as TL
import Network.Mail.Mime (Address (..), Mail, plainPart, simpleMail')
import Network.Mail.SMTP (sendMailWithLoginTLS)
import Notification.Config (SmtpConfig (..))
import Notification.Domain.Email (EmailMessage (..))
import Notification.Ports.EmailSender (EmailSender (..))

newtype SmtpEmailM a = SmtpEmailM
  { unSmtpEmailM :: ReaderT SmtpConfig IO a }
  deriving (Functor, Applicative, Monad)

runSmtpEmailM :: SmtpConfig -> SmtpEmailM a -> IO a
runSmtpEmailM cfg m = runReaderT (unSmtpEmailM m) cfg

instance EmailSender SmtpEmailM where
  sendEmail msg = SmtpEmailM $ do
    cfg <- ask
    let mail :: Mail
        mail = simpleMail'
                 (Address Nothing (emTo msg))
                 (Address (Just (smtpFromName cfg)) (smtpFromAddr cfg))
                 (emSubject msg)
                 (TL.fromStrict (emBody msg))
    result <- liftIO $ try @SomeException $
      sendMailWithLoginTLS
        (smtpHost cfg)
        (smtpUser cfg)
        (smtpPass cfg)
        mail
    pure $ case result of
      Left err -> Left (show err)
      Right _  -> Right ()
