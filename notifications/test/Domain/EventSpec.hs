module Domain.EventSpec (spec) where

import Data.Aeson (decode, encode)
import Data.Time (UTCTime (..), fromGregorian)
import Test.Hspec

import Notification.Domain.Event (EventPayload (..))

t :: UTCTime
t = UTCTime (fromGregorian 2026 8 6) 0

spec :: Spec
spec = describe "EventPayload JSON" $ do

  it "round-trips UserRegistered" $
    decode (encode (UserRegistered "a" "Adam" "a@b.com" t))
      `shouldBe` Just (UserRegistered "a" "Adam" "a@b.com" t)

  it "round-trips UserEnrolled" $
    decode (encode (UserEnrolled "u" "Jane" "j@b.com" "c" "Haskell" t))
      `shouldBe` Just (UserEnrolled "u" "Jane" "j@b.com" "c" "Haskell" t)

  it "round-trips RequestReceived" $
    decode (encode (RequestReceived "co" "r" "Alice" "a" "Bob" "b@x.com" t))
      `shouldBe` Just (RequestReceived "co" "r" "Alice" "a" "Bob" "b@x.com" t)

  it "round-trips RequestAccepted" $
    decode (encode (RequestAccepted "co" "r" "Alice" "a@x.com" "a" "Bob" t))
      `shouldBe` Just (RequestAccepted "co" "r" "Alice" "a@x.com" "a" "Bob" t)
