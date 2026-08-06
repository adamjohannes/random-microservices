module Spec (main) where

import Test.Hspec
import qualified Adapters.SmtpEmailSpec as SmtpEmail
import qualified Domain.DispatchSpec as Dispatch
import qualified Domain.EventSpec as Event

main :: IO ()
main = hspec $ do
  Dispatch.spec
  Event.spec
  SmtpEmail.spec
