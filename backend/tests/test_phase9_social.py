"""Phase 9 integration tests: social feed endpoint."""

from __future__ import annotations

from secrets import token_hex
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app.main import app
from tests.helpers import register_or_login_as_admin


def _register_and_login(client: TestClient, prefix: str) -> dict[str, str]:
    suffix = token_hex(4)
    username = f"{prefix}_{suffix}"
    email = f"{username}@example.com"
    password = "password123"

    return register_or_login_as_admin(client, username, email, password)


def _existing_media_id(client: TestClient, headers: dict[str, str]) -> str:
    """Return an existing media ID (seeded by conftest pytest_sessionstart)."""
    res = client.get("/api/v1/media/popular?limit=1", headers=headers)
    assert res.status_code == 200, res.text
    items = res.json().get("items", [])
    assert items, "Expected media entries seeded by conftest; run conftest.pytest_sessionstart first"
    return items[0]["id"]


def test_phase9_social_feed_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/social/feed")
        assert res.status_code == 401


def test_phase9_social_feed_returns_shared_group_member_activity_only() -> None:
    with TestClient(app) as client:
        viewer = _register_and_login(client, "viewer")
        friend = _register_and_login(client, "friend")
        outsider = _register_and_login(client, "outsider")

        viewer_headers = {"Authorization": f"Bearer {viewer['access_token']}"}
        friend_headers = {"Authorization": f"Bearer {friend['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Phase9 Group", "description": "social feed test", "is_private": True},
            headers=viewer_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=friend_headers)
        assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, viewer_headers)

        # Friend activity should appear in viewer feed.
        friend_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 3},
            headers=friend_headers,
        )
        assert friend_entry.status_code == 201, friend_entry.text

        # Viewer own activity should be excluded from feed.
        viewer_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 1},
            headers=viewer_headers,
        )
        assert viewer_entry.status_code == 201, viewer_entry.text

        # Outsider activity should be excluded from feed.
        outsider_entry = client.post(
            "/api/v1/lists",
            json={"media_id": media_id, "status": "watching", "progress": 10},
            headers=outsider_headers,
        )
        assert outsider_entry.status_code == 201, outsider_entry.text

        feed_res = client.get("/api/v1/social/feed", headers=viewer_headers)
        assert feed_res.status_code == 200, feed_res.text

        body = feed_res.json()
        assert "items" in body
        assert isinstance(body["items"], list)
        assert body["total"] >= 1

        actor_ids = {item["user_id"] for item in body["items"]}
        assert friend["user_id"] in actor_ids
        assert viewer["user_id"] not in actor_ids
        assert outsider["user_id"] not in actor_ids


def test_phase9_recommend_requires_shared_group_and_prevents_self() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "sender")
        receiver = _register_and_login(client, "receiver")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}

        # self-recommendation is invalid
        self_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": sender["user_id"], "media_id": str(uuid4()), "message": "watch this"},
            headers=sender_headers,
        )
        assert self_res.status_code == 400, self_res.text

        # recommendation without shared group is invalid
        no_group_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": str(uuid4()), "message": "watch this"},
            headers=sender_headers,
        )
        assert no_group_res.status_code == 400, no_group_res.text


def test_phase9_recommend_creates_recommendation_for_shared_group_member() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "senderok")
        receiver = _register_and_login(client, "receiverok")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}
        receiver_headers = {"Authorization": f"Bearer {receiver['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Recommend Group", "description": "phase 9.2", "is_private": True},
            headers=sender_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=receiver_headers)
        assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, sender_headers)

        rec_res = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "you will like this"},
            headers=sender_headers,
        )
        assert rec_res.status_code == 201, rec_res.text
        body = rec_res.json()
        assert body["from_user_id"] == sender["user_id"]
        assert body["to_user_id"] == receiver["user_id"]
        assert body["is_acknowledged"] is False


def test_phase9_recommendation_inbox_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/social/recommendations/inbox")
        assert res.status_code == 401


def test_phase9_recommendation_inbox_returns_only_current_user_items() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "senderinbox")
        receiver = _register_and_login(client, "receiverinbox")
        third = _register_and_login(client, "thirdinbox")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}
        receiver_headers = {"Authorization": f"Bearer {receiver['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Inbox Group", "description": "phase 9.3", "is_private": True},
            headers=sender_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_receiver = client.post(f"/api/v1/groups/join/{invite_code}", headers=receiver_headers)
        assert join_receiver.status_code == 200, join_receiver.text

        media_id = _existing_media_id(client, sender_headers)

        # sender -> receiver (should appear in receiver inbox)
        rec_ok = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "for receiver"},
            headers=sender_headers,
        )
        assert rec_ok.status_code == 201, rec_ok.text

        # sender -> third user in another shared group (must NOT appear in receiver inbox)
        group_create_2 = client.post(
            "/api/v1/groups",
            json={"name": "Other Group", "description": "phase 9.3 other", "is_private": True},
            headers=sender_headers,
        )
        assert group_create_2.status_code == 201, group_create_2.text
        invite_code_2 = group_create_2.json()["invite_code"]
        third_headers = {"Authorization": f"Bearer {third['access_token']}"}
        join_third = client.post(f"/api/v1/groups/join/{invite_code_2}", headers=third_headers)
        assert join_third.status_code == 200, join_third.text

        rec_other = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": third["user_id"], "media_id": media_id, "message": "for third"},
            headers=sender_headers,
        )
        assert rec_other.status_code == 201, rec_other.text

        inbox_res = client.get("/api/v1/social/recommendations/inbox", headers=receiver_headers)
        assert inbox_res.status_code == 200, inbox_res.text
        body = inbox_res.json()

        assert isinstance(body["items"], list)
        assert body["total"] >= 1
        assert body["limit"] == 50
        assert body["offset"] == 0

        recipients = {item["to_user_id"] for item in body["items"]}
        assert recipients == {receiver["user_id"]}


def test_phase9_acknowledge_recommendation_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.patch(f"/api/v1/social/recommendations/{uuid4()}/acknowledge")
        assert res.status_code == 401


def test_phase9_acknowledge_recommendation_happy_path_and_ownership() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "senderack")
        receiver = _register_and_login(client, "receiverack")
        outsider = _register_and_login(client, "outsiderack")

        sender_headers = {"Authorization": f"Bearer {sender['access_token']}"}
        receiver_headers = {"Authorization": f"Bearer {receiver['access_token']}"}
        outsider_headers = {"Authorization": f"Bearer {outsider['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Ack Group", "description": "phase 9.4", "is_private": True},
            headers=sender_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]

        join_receiver = client.post(f"/api/v1/groups/join/{invite_code}", headers=receiver_headers)
        assert join_receiver.status_code == 200, join_receiver.text

        media_id = _existing_media_id(client, sender_headers)

        rec = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "ack me"},
            headers=sender_headers,
        )
        assert rec.status_code == 201, rec.text
        rec_id = rec.json()["id"]

        # outsider cannot acknowledge someone else's recommendation
        outsider_ack = client.patch(
            f"/api/v1/social/recommendations/{rec_id}/acknowledge",
            headers=outsider_headers,
        )
        assert outsider_ack.status_code == 404, outsider_ack.text

        # receiver acknowledges successfully
        ack = client.patch(
            f"/api/v1/social/recommendations/{rec_id}/acknowledge",
            headers=receiver_headers,
        )
        assert ack.status_code == 200, ack.text
        body = ack.json()
        assert body["id"] == rec_id
        assert body["is_acknowledged"] is True
        assert body["acknowledged_at"] is not None


def test_phase9_create_discussion_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/social/discussions",
            json={
                "media_id": str(uuid4()),
                "group_id": str(uuid4()),
                "title": "hello",
                "body": "discussion body",
            },
        )
        assert res.status_code == 401


def test_phase9_create_discussion_requires_group_membership() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerdisc")
        stranger = _register_and_login(client, "strangerdisc")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        stranger_headers = {"Authorization": f"Bearer {stranger['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Discussion Group", "description": "phase 9.5", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        group_id = group_create.json()["id"]

        res = client.post(
            "/api/v1/social/discussions",
            json={
                "media_id": str(uuid4()),
                "group_id": group_id,
                "title": "unauthorized",
                "body": "should fail",
            },
            headers=stranger_headers,
        )
        assert res.status_code == 403, res.text


def test_phase9_create_discussion_returns_400_when_media_not_seeded() -> None:
    with TestClient(app) as client:
        owner = _register_and_login(client, "ownerdisc2")
        member = _register_and_login(client, "memberdisc2")

        owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
        member_headers = {"Authorization": f"Bearer {member['access_token']}"}

        group_create = client.post(
            "/api/v1/groups",
            json={"name": "Discussion Group 2", "description": "phase 9.5", "is_private": True},
            headers=owner_headers,
        )
        assert group_create.status_code == 201, group_create.text
        invite_code = group_create.json()["invite_code"]
        group_id = group_create.json()["id"]

        join_member = client.post(f"/api/v1/groups/join/{invite_code}", headers=member_headers)
        assert join_member.status_code == 200, join_member.text

        # Current test DB may not have media seeded. We expect graceful 400 instead of 500.
        res = client.post(
            "/api/v1/social/discussions",
            json={
                "media_id": str(uuid4()),
                "group_id": group_id,
                "title": "seed pending",
                "body": "discussion should wait for sync",
            },
            headers=member_headers,
        )
        assert res.status_code == 400, res.text


def test_phase9_get_discussions_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get(f"/api/v1/social/discussions/{uuid4()}")
        assert res.status_code == 401


def test_phase9_get_discussions_returns_empty_when_no_seeded_media_data() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "readerdisc")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get(f"/api/v1/social/discussions/{uuid4()}?limit=20&offset=0", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["items"] == []
        assert body["total"] == 0
        assert body["limit"] == 20
        assert body["offset"] == 0


def test_phase9_create_discussion_reply_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.post(
            f"/api/v1/social/discussions/{uuid4()}/replies",
            json={"body": "hello reply"},
        )
        assert res.status_code == 401


def test_phase9_create_discussion_reply_returns_404_for_missing_discussion() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "replyuser")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.post(
            f"/api/v1/social/discussions/{uuid4()}/replies",
            json={"body": "missing discussion"},
            headers=headers,
        )
        assert res.status_code == 404, res.text


def test_phase9_public_profile_by_username_success_and_no_email_field() -> None:
    with TestClient(app) as client:
        user = _register_and_login(client, "publicprofile")

        me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {user['access_token']}"})
        assert me.status_code == 200, me.text
        username = me.json()["username"]

        res = client.get(f"/api/v1/users/{username}/profile")
        assert res.status_code == 200, res.text
        body = res.json()

        assert body["username"] == username
        assert "email" not in body


def test_phase9_public_profile_by_username_not_found() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/users/nonexistent_user_123/profile")
        assert res.status_code == 404


# --- Sent Recommendations ---


def test_phase9_recommendations_sent_requires_auth() -> None:
    with TestClient(app) as client:
        res = client.get("/api/v1/social/recommendations/sent")
        assert res.status_code == 401


def test_phase9_recommendations_sent_returns_only_sent_by_user() -> None:
    with TestClient(app) as client:
        sender1 = _register_and_login(client, "sent1")
        sender2 = _register_and_login(client, "sent2")
        receiver = _register_and_login(client, "sentrecv")

        h1 = {"Authorization": f"Bearer {sender1['access_token']}"}
        h2 = {"Authorization": f"Bearer {sender2['access_token']}"}
        hr = {"Authorization": f"Bearer {receiver['access_token']}"}

        # Create shared group
        group = client.post(
            "/api/v1/groups",
            json={"name": "Sent Test", "description": "sent recs", "is_private": True},
            headers=h1,
        )
        assert group.status_code == 201, group.text
        invite_code = group.json()["invite_code"]

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=h2)
        assert join_res.status_code == 200, join_res.text

        join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=hr)
        assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, h1)

        # sender1 -> receiver
        rec1 = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "from1"},
            headers=h1,
        )
        assert rec1.status_code == 201, rec1.text

        # sender2 -> receiver
        rec2 = client.post(
            "/api/v1/social/recommend",
            json={"to_user_id": receiver["user_id"], "media_id": media_id, "message": "from2"},
            headers=h2,
        )
        assert rec2.status_code == 201, rec2.text

        # sender1 sent recs should contain only rec1
        sent1_resp = client.get("/api/v1/social/recommendations/sent", headers=h1)
        assert sent1_resp.status_code == 200, sent1_resp.text
        body = sent1_resp.json()
        assert body["total"] >= 1
        assert body["limit"] == 50
        assert body["offset"] == 0
        for item in body["items"]:
            assert item["from_user_id"] == sender1["user_id"]

        # sender2 sent recs should contain only rec2
        sent2_resp = client.get("/api/v1/social/recommendations/sent", headers=h2)
        assert sent2_resp.status_code == 200, sent2_resp.text
        body2 = sent2_resp.json()
        assert body2["total"] >= 1
        for item in body2["items"]:
            assert item["from_user_id"] == sender2["user_id"]


def test_phase9_recommendations_sent_pagination() -> None:
    with TestClient(app) as client:
        sender = _register_and_login(client, "sentpage")
        receiver1 = _register_and_login(client, "sentpagercv1")
        receiver2 = _register_and_login(client, "sentpagercv2")
        receiver3 = _register_and_login(client, "sentpagercv3")

        h = {"Authorization": f"Bearer {sender['access_token']}"}
        hr1 = {"Authorization": f"Bearer {receiver1['access_token']}"}
        hr2 = {"Authorization": f"Bearer {receiver2['access_token']}"}
        hr3 = {"Authorization": f"Bearer {receiver3['access_token']}"}

        group = client.post(
            "/api/v1/groups",
            json={"name": "Sent Page", "description": "sent pagination", "is_private": True},
            headers=h,
        )
        assert group.status_code == 201, group.text
        invite_code = group.json()["invite_code"]
        for hr in (hr1, hr2, hr3):
            join_res = client.post(f"/api/v1/groups/join/{invite_code}", headers=hr)
            assert join_res.status_code == 200, join_res.text

        media_id = _existing_media_id(client, h)

        receivers = [receiver1, receiver2, receiver3]
        # Create 3 sent recommendations to 3 different users (unique constraint)
        for idx, rcv in enumerate(receivers):
            rec = client.post(
                "/api/v1/social/recommend",
                json={
                    "to_user_id": rcv["user_id"],
                    "media_id": media_id,
                    "message": f"page_{idx}",
                },
                headers=h,
            )
            assert rec.status_code == 201, rec.text

        # First page: limit=2
        page1 = client.get("/api/v1/social/recommendations/sent?limit=2&offset=0", headers=h)
        assert page1.status_code == 200, page1.text
        body1 = page1.json()
        assert len(body1["items"]) == 2
        assert body1["total"] >= 3
        assert body1["limit"] == 2
        assert body1["offset"] == 0

        # Second page: offset=2
        page2 = client.get("/api/v1/social/recommendations/sent?limit=2&offset=2", headers=h)
        assert page2.status_code == 200, page2.text
        body2 = page2.json()
        assert len(body2["items"]) >= 1
        assert body2["offset"] == 2

        # Items should differ between pages (different IDs)
        ids1 = {item["id"] for item in body1["items"]}
        ids2 = {item["id"] for item in body2["items"]}
        assert ids1.isdisjoint(ids2), "Pages should return different items"


def test_phase9_recommendations_sent_empty_for_user_with_no_sent() -> None:
    """A user who has never sent a recommendation gets an empty list."""
    with TestClient(app) as client:
        user = _register_and_login(client, "sentempty")
        h = {"Authorization": f"Bearer {user['access_token']}"}

        resp = client.get("/api/v1/social/recommendations/sent", headers=h)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["items"] == []
        assert body["total"] == 0


def test_phase9_discussion_replies_requires_auth() -> None:
    """Discussion replies endpoint requires authentication."""
    with TestClient(app) as client:
        res = client.get(f"/api/v1/social/discussions/{uuid4()}/replies")
        assert res.status_code == 401


def test_phase9_discussion_replies_not_found_for_random_uuid() -> None:
    """A non-existent discussion returns 404."""
    with TestClient(app) as client:
        user = _register_and_login(client, "discreply_nf")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get(f"/api/v1/social/discussions/{uuid4()}/replies", headers=headers)
        assert res.status_code == 404, res.text


def test_phase9_discussion_replies_returns_replies_for_group_member() -> None:
    """A group member can see discussion replies."""
    with TestClient(app) as client:
        host = _register_and_login(client, "discreply_host")
        member = _register_and_login(client, "discreply_member")
        host_h = {"Authorization": f"Bearer {host['access_token']}"}
        member_h = {"Authorization": f"Bearer {member['access_token']}"}

        # Create a group
        g_res = client.post(
            "/api/v1/groups",
            json={"name": "ReplyTestGroup", "description": "", "is_private": False},
            headers=host_h,
        )
        assert g_res.status_code == 201, g_res.text
        invite = g_res.json()["invite_code"]

        # Join member
        join_res = client.post(f"/api/v1/groups/join/{invite}", headers=member_h)
        assert join_res.status_code == 200, join_res.text

        # Get a media ID
        media_id = _existing_media_id(client, host_h)

        # Create discussion
        d_res = client.post(
            "/api/v1/social/discussions",
            headers=host_h,
            json={
                "media_id": media_id,
                "group_id": g_res.json()["id"],
                "body": "What do you think?",
            },
        )
        assert d_res.status_code == 201, d_res.text
        discussion_id = d_res.json()["id"]

        # Host creates a reply
        r_res = client.post(
            f"/api/v1/social/discussions/{discussion_id}/replies",
            headers=host_h,
            json={"body": "I think it's great!"},
        )
        assert r_res.status_code == 201, r_res.text

        # Member fetches replies
        res = client.get(
            f"/api/v1/social/discussions/{discussion_id}/replies",
            headers=member_h,
        )
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["total"] >= 1
        assert any("great" in r.get("body", "") for r in body["items"])
        assert "items" in body


def test_phase9_discussion_replies_empty_for_discussion_with_no_replies() -> None:
    """A discussion with no replies returns empty list."""
    with TestClient(app) as client:
        user = _register_and_login(client, "discreply_empty")
        h = {"Authorization": f"Bearer {user['access_token']}"}

        # Create group
        g_res = client.post(
            "/api/v1/groups",
            json={"name": "EmptyReplyGroup", "description": "", "is_private": False},
            headers=h,
        )
        assert g_res.status_code == 201, g_res.text
        group_id = g_res.json()["id"]

        media_id = _existing_media_id(client, h)

        # Create discussion
        d_res = client.post(
            "/api/v1/social/discussions",
            headers=h,
            json={"media_id": media_id, "group_id": group_id, "body": "Test"},
        )
        assert d_res.status_code == 201, d_res.text
        disc_id = d_res.json()["id"]

        res = client.get(f"/api/v1/social/discussions/{disc_id}/replies", headers=h)
        assert res.status_code == 200, res.text
        assert res.json()["items"] == []


def test_phase9_media_relations_requires_auth() -> None:
    """Media relations endpoint requires auth."""
    with TestClient(app) as client:
        res = client.get(f"/api/v1/media/{uuid4()}/relations")
        assert res.status_code == 401


def test_phase9_media_relations_empty_for_random_media() -> None:
    """A random media UUID returns 200 with empty relations list."""
    with TestClient(app) as client:
        user = _register_and_login(client, "mediarel")
        headers = {"Authorization": f"Bearer {user['access_token']}"}

        res = client.get(f"/api/v1/media/{uuid4()}/relations", headers=headers)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["items"] == []
