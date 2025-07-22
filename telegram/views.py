from django.shortcuts import render

# Create your views here.
# TELEGRAM_URL_RE = re.compile(
#     r"^https?://t\.me/(c/)?([^/]+)/(\d+)/?$",
#     re.IGNORECASE
# )
#
# # Telegram Client singleton
# _client = None
#
#
# def get_client():
#     global _client
#     if _client is None:
#         _client = TelegramClient(
#             getattr(settings, "TELEGRAM_SESSION_NAME", "tg_session"),
#             settings.TELEGRAM_API_ID,
#             settings.TELEGRAM_API_HASH,
#         )
#     return _client
#
#
# def parse_telegram_url(url: str):
#     m = TELEGRAM_URL_RE.match(url.strip())
#     print(115, m)
#     if not m:
#         raise ValueError("Noto'g'ri Telegram URL")
#     c_prefix, name_or_id, msg_id = m.groups()
#     username_like = ("c/" + name_or_id) if c_prefix else name_or_id
#     return username_like, int(msg_id) if msg_id else None


# class STelegramBackfillAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     @extend_schema(
#         request=STelegramBackfillSerializer,
#         responses={
#             201: {
#                 'type': 'object',
#                 'properties': {
#                     "requested": 123,
#                     "fetched_from_telegram": 12,
#                     "saved_to_db": 11,
#                 }
#             }
#         },
#         description="Yangi Order yaratadi va unga Linkni bir vaqtda bog‘laydi"
#     )
#     async def post(self, request, *args, **kwargs):
#         """
#         JSON:
#         {
#           "order_id": 123,
#           "url": "https://t.me/somechannel/4567",
#           "count": 50
#         }
#         """
#         order_id = request.data.get("order_id")
#         url = request.data.get("url")
#         count = int(request.data.get("count", 50))
#
#         if not order_id or not url:
#             return Response({"detail": "order_id va url majburiy."}, status=status.HTTP_400_BAD_REQUEST)
#
#         order = await sync_to_async(get_object_or_404)(Order, pk=order_id)
#
#         username_like, ref_msg_id = parse_telegram_url(url)
#         if ref_msg_id is None:
#             return Response({"detail": "URL message_id topilmadi"}, status=status.HTTP_400_BAD_REQUEST)
#
#         client = get_client()
#         await client.connect()
#         if not await client.is_user_authorized():
#             await client.start()  # bir marta interaktiv avtorizatsiya qilgan bo'lishingiz shart
#
#         try:
#             entity = await client.get_entity(username_like)
#         except Exception as e:
#             return Response({"detail": f"Kanalni olishda xatolik: {str(e)}"}, status=400)
#
#         # oldindan mavjud linklarni olish
#         existing_links = set(await sync_to_async(list)(
#             Link.objects.filter(order=order).values_list("link", flat=True)
#         ))
#
#         # Telegramdan eski xabarlarni olish
#         saved_links = []
#         fetched = 0
#         async for msg in client.iter_messages(entity, offset_id=ref_msg_id, limit=count):
#             fetched += 1
#             post_url = f"https://t.me/{username_like.split('/', 1)[-1]}/{msg.id}"
#             if post_url not in existing_links:
#                 saved_links.append(Link(order=order, link=post_url))
#                 existing_links.add(post_url)
#
#         if saved_links:
#             await sync_to_async(Link.objects.bulk_create)(saved_links)
#
#         return Response({
#             "requested": count,
#             "fetched_from_telegram": fetched,
#             "saved_to_db": len(saved_links),
#         }, status=200)
# --- Asinxron ish: Telegramdan xabarlarni olib Link ga yozish ---
# async def process_backfill(order, url, count):
#     client = get_client()
#     await client.connect()
#     if not await client.is_user_authorized():
#         await client.start()  # Session oldindan autentifikatsiya qilingan bo‘lishi kerak
#
#     print(199, url)
#     username_like, ref_msg_id = parse_telegram_url(url)
#     if ref_msg_id is None:
#         raise ValueError("URL message_id o'z ichiga olmaydi.")
#
#     entity = await client.get_entity(username_like)
#
#     # Mavjud linklarni cache qilib olamiz (bir order uchun)
#     existing_links = set(
#         Link.objects.filter(order=order)
#         .values_list("link", flat=True)
#     )
#
#     saved_links = []
#     fetched = 0
#     async for msg in client.iter_messages(entity, offset_id=ref_msg_id, limit=count):
#         fetched += 1
#         post_url = f"https://t.me/{username_like.split('/', 1)[-1]}/{msg.id}"
#         if post_url not in existing_links:
#             saved_links.append(Link(order=order, link=post_url))
#             existing_links.add(post_url)
#
#     if saved_links:
#         Link.objects.bulk_create(saved_links)
#
#     return {
#         "requested": count,
#         "fetched_from_telegram": fetched,
#         "saved_to_db": len(saved_links),
#     }
