module Adapters.SmtpEmailSpec (spec) where

import Control.Monad.Trans.Writer (WriterT, runWriterT, tell)
import Data.Functor.Identity (Identity, runIdentity)
import Data.Time (UTCTime (..), fromGregorian)
import Test.Hspec

import Notification.Domain.Dispatch (dispatch)
import Notification.Domain.Email (EmailMessage (..))
import Notification.Domain.Event (EventPayload (..))
import Notification.Ports.EmailSender (EmailSender (..))

-- Pure test double: captures sent messages in a Writer
newtype TestEmailM a = TestEmailM
  { runTestEmail :: WriterT [EmailMessage] Identity a }
  deriving (Functor, Applicative, Monad)

instance EmailSender TestEmailM where
  sendEmail msg = TestEmailM $ do
    tell [msg]
    pure (Right ())

runTest :: TestEmailM a -> ([EmailMessage], a)
runTest m =
  let (a, msgs) = runIdentity (runWriterT (runTestEmail m))
  in (msgs, a)

t :: UTCTime
t = UTCTime (fromGregorian 2026 8 6) 0

spec :: Spec
spec = describe "EmailSender (TestEmailM)" $ do

  it "captures sent email" $ do
    let Just msg = dispatch (UserRegistered "a" "Adam" "a@b.com" t)
        (captured, result) = runTest (sendEmail msg)
    result `shouldBe` Right ()
    length captured `shouldBe` 1
    emTo (head captured) `shouldBe` "a@b.com"

  it "captures correct subject for enrollment" $ do
    let Just msg = dispatch (UserEnrolled "u" "Jane" "j@b.com" "c" "Haskell 101" t)
        (captured, _) = runTest (sendEmail msg)
    emSubject (head captured) `shouldBe` "You've enrolled in \"Haskell 101\""
