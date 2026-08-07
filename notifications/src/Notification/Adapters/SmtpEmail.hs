module Notification.Adapters.SmtpEmail
  ( SmtpEmailM (..)
  , runSmtpEmailM
  ) where

import Control.Exception (SomeException, try)
import Control.Monad.IO.Class (liftIO)
import Control.Monad.Reader (ReaderT, ask, runReaderT)
import qualified Data.ByteString.Lazy as BL
import qualified Data.Text as T
import qualified Data.Text.Lazy as TL
import Network.HaskellNet.SMTP (doSMTPPort, sendMimeMail2)
import Network.Mail.Mime (Address (..), Mail, renderMail', simpleMail')
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
        port = fromIntegral (smtpPort cfg)
    result <- liftIO $ try @SomeException $
      doSMTPPort (smtpHost cfg) port $ \conn ->
        sendMimeMail2 mail conn
    pure $ case result of
      Left err -> Left (show err)
      Right _  -> Right ()
