module Notification.Domain.Event (EventPayload (..)) where

import Data.Aeson (FromJSON (..), ToJSON (..), object, withObject, (.:), (.=))
import Data.Text (Text)
import Data.Time (UTCTime)

data EventPayload
  = UserRegistered
      { erAccountId  :: Text
      , erName       :: Text
      , erEmail      :: Text
      , erOccurredAt :: UTCTime
      }
  | UserEnrolled
      { ueUserId      :: Text
      , ueUserName    :: Text
      , ueUserEmail   :: Text
      , ueCourseId    :: Text
      , ueCourseTitle :: Text
      , ueOccurredAt  :: UTCTime
      }
  | RequestReceived
      { rrConnectionId   :: Text
      , rrRequesterId    :: Text
      , rrRequesterName  :: Text
      , rrAddresseeId    :: Text
      , rrAddresseeName  :: Text
      , rrAddresseeEmail :: Text
      , rrOccurredAt     :: UTCTime
      }
  | RequestAccepted
      { raConnectionId   :: Text
      , raRequesterId    :: Text
      , raRequesterName  :: Text
      , raRequesterEmail :: Text
      , raAddresseeId    :: Text
      , raAddresseeName  :: Text
      , raOccurredAt     :: UTCTime
      }
  deriving (Show, Eq)

instance FromJSON EventPayload where
  parseJSON = withObject "EventPayload" $ \o -> do
    eventType <- o .: "event_type" :: _ Text
    case eventType of
      "account.user_registered" ->
        UserRegistered
          <$> o .: "account_id"
          <*> o .: "name"
          <*> o .: "email"
          <*> o .: "occurred_at"
      "course.user_enrolled" ->
        UserEnrolled
          <$> o .: "user_id"
          <*> o .: "user_name"
          <*> o .: "user_email"
          <*> o .: "course_id"
          <*> o .: "course_title"
          <*> o .: "occurred_at"
      "connections.request_received" ->
        RequestReceived
          <$> o .: "connection_id"
          <*> o .: "requester_id"
          <*> o .: "requester_name"
          <*> o .: "addressee_id"
          <*> o .: "addressee_name"
          <*> o .: "addressee_email"
          <*> o .: "occurred_at"
      "connections.request_accepted" ->
        RequestAccepted
          <$> o .: "connection_id"
          <*> o .: "requester_id"
          <*> o .: "requester_name"
          <*> o .: "requester_email"
          <*> o .: "addressee_id"
          <*> o .: "addressee_name"
          <*> o .: "occurred_at"
      other -> fail $ "unknown event_type: " <> show other

instance ToJSON EventPayload where
  toJSON (UserRegistered aid name email occ) = object
    [ "event_type"  .= ("account.user_registered" :: Text)
    , "account_id"  .= aid
    , "name"        .= name
    , "email"       .= email
    , "occurred_at" .= occ
    ]
  toJSON (UserEnrolled uid uname uemail cid ctitle occ) = object
    [ "event_type"   .= ("course.user_enrolled" :: Text)
    , "user_id"      .= uid
    , "user_name"    .= uname
    , "user_email"   .= uemail
    , "course_id"    .= cid
    , "course_title" .= ctitle
    , "occurred_at"  .= occ
    ]
  toJSON (RequestReceived cid rid rname aid aname aemail occ) = object
    [ "event_type"      .= ("connections.request_received" :: Text)
    , "connection_id"   .= cid
    , "requester_id"    .= rid
    , "requester_name"  .= rname
    , "addressee_id"    .= aid
    , "addressee_name"  .= aname
    , "addressee_email" .= aemail
    , "occurred_at"     .= occ
    ]
  toJSON (RequestAccepted cid rid rname remail aid aname occ) = object
    [ "event_type"      .= ("connections.request_accepted" :: Text)
    , "connection_id"   .= cid
    , "requester_id"    .= rid
    , "requester_name"  .= rname
    , "requester_email" .= remail
    , "addressee_id"    .= aid
    , "addressee_name"  .= aname
    , "occurred_at"     .= occ
    ]
