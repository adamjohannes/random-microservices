module Notification.Domain.Dispatch (dispatch) where

import Notification.Domain.Email (EmailMessage (..))
import Notification.Domain.Event (EventPayload (..))
import qualified Data.Text as T

dispatch :: EventPayload -> Maybe EmailMessage
dispatch (UserRegistered _ name email _) = Just EmailMessage
  { emTo      = email
  , emSubject = "Welcome to the platform, " <> name <> "!"
  , emBody    = T.unlines
      [ "Hi " <> name <> ","
      , ""
      , "Your account has been created successfully. Welcome aboard!"
      ]
  }
dispatch (UserEnrolled _ name email _ courseTitle _) = Just EmailMessage
  { emTo      = email
  , emSubject = "You've enrolled in \"" <> courseTitle <> "\""
  , emBody    = T.unlines
      [ "Hi " <> name <> ","
      , ""
      , "You have successfully enrolled in \"" <> courseTitle <> "\"."
      , "You can now access the course content."
      ]
  }
dispatch (RequestReceived _ _ requesterName _ addresseeName addresseeEmail _) = Just EmailMessage
  { emTo      = addresseeEmail
  , emSubject = requesterName <> " sent you a connection request"
  , emBody    = T.unlines
      [ "Hi " <> addresseeName <> ","
      , ""
      , requesterName <> " would like to connect with you."
      , "Log in to accept or reject the request."
      ]
  }
dispatch (RequestAccepted _ _ requesterName requesterEmail _ addresseeName _) = Just EmailMessage
  { emTo      = requesterEmail
  , emSubject = addresseeName <> " accepted your connection request"
  , emBody    = T.unlines
      [ "Hi " <> requesterName <> ","
      , ""
      , addresseeName <> " has accepted your connection request."
      , "You are now connected."
      ]
  }
