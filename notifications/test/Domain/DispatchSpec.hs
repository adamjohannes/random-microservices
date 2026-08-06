module Domain.DispatchSpec (spec) where

import Data.Time (UTCTime, fromGregorian, UTCTime (..))
import Test.Hspec

import Notification.Domain.Dispatch (dispatch)
import Notification.Domain.Email (EmailMessage (..))
import Notification.Domain.Event (EventPayload (..))

sampleTime :: UTCTime
sampleTime = UTCTime (fromGregorian 2026 8 6) 0

spec :: Spec
spec = describe "dispatch" $ do

  describe "UserRegistered" $ do
    let evt = UserRegistered "acc-1" "Adam Johannes" "adam@example.com" sampleTime
    it "returns Just" $
      dispatch evt `shouldSatisfy` \r -> case r of Just _ -> True; _ -> False
    it "addresses email to registrant" $
      fmap emTo (dispatch evt) `shouldBe` Just "adam@example.com"
    it "subject contains name" $
      fmap emSubject (dispatch evt) `shouldBe` Just "Welcome to the platform, Adam Johannes!"
    it "body mentions name" $
      fmap (("Adam Johannes" `elem`) . words . emBody) (dispatch evt) `shouldBe` Just True

  describe "UserEnrolled" $ do
    let evt = UserEnrolled "u-1" "Jane Doe" "jane@example.com" "c-1" "Intro to Haskell" sampleTime
    it "returns Just" $
      dispatch evt `shouldSatisfy` \r -> case r of Just _ -> True; _ -> False
    it "addresses email to enrolled user" $
      fmap emTo (dispatch evt) `shouldBe` Just "jane@example.com"
    it "subject contains course title" $
      fmap emSubject (dispatch evt) `shouldBe` Just "You've enrolled in \"Intro to Haskell\""
    it "body mentions course title" $
      fmap (("Haskell" `elem`) . words . emBody) (dispatch evt) `shouldBe` Just True

  describe "RequestReceived" $ do
    let evt = RequestReceived "conn-1" "req-1" "Alice" "addr-1" "Bob" "bob@example.com" sampleTime
    it "returns Just" $
      dispatch evt `shouldSatisfy` \r -> case r of Just _ -> True; _ -> False
    it "addresses email to addressee" $
      fmap emTo (dispatch evt) `shouldBe` Just "bob@example.com"
    it "subject contains requester name" $
      fmap emSubject (dispatch evt) `shouldBe` Just "Alice sent you a connection request"
    it "body mentions addressee name" $
      fmap (("Bob," `elem`) . words . emBody) (dispatch evt) `shouldBe` Just True

  describe "RequestAccepted" $ do
    let evt = RequestAccepted "conn-1" "req-1" "Alice" "alice@example.com" "addr-1" "Bob" sampleTime
    it "returns Just" $
      dispatch evt `shouldSatisfy` \r -> case r of Just _ -> True; _ -> False
    it "addresses email to requester" $
      fmap emTo (dispatch evt) `shouldBe` Just "alice@example.com"
    it "subject contains addressee name" $
      fmap emSubject (dispatch evt) `shouldBe` Just "Bob accepted your connection request"
    it "body mentions requester name" $
      fmap (("Alice," `elem`) . words . emBody) (dispatch evt) `shouldBe` Just True
