# 後端 API 修正紀錄

這份文件記錄了後端需要補上的兩項重要修正。請負責後端的同學參考以下內容進行程式碼修改，或是直接將 GitHub 上的 `fix-game-deletion` 分支透過 Pull Request 合併進 `main` 分支。

---

## 修正一：參與名單新增「歲數」與「等級」

為了讓前端可以在「參與名單」視窗中正確顯示使用者的歲數 (age) 與該球局對應的運動等級 (level)，我們需要修改 `GameMatchSerializer` 中的 `participants` 所使用的序列化器。

### 修改目標檔案
`backend/api_v1/serializers.py`

### 具體程式碼變更

找到 `MatchParticipantUserSerializer` 這個類別，**替換成以下程式碼**：

```python
class MatchParticipantUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    phone = serializers.ReadOnlyField(source='user.phone')
    name = serializers.ReadOnlyField(source='user.name')
    age = serializers.ReadOnlyField(source='user.age')
    level = serializers.SerializerMethodField()

    class Meta:
        model = MatchParticipant
        fields = ('id', 'phone', 'name', 'age', 'level')

    def get_level(self, obj):
        user = obj.user
        match = obj.match
        
        # 確保球局和運動分類存在
        if not match or not match.sport:
            return 'C'
            
        # 尋找該使用者對應此球局運動的等級紀錄
        sport_level = user.sport_levels.filter(sport=match.sport).first()
        
        if sport_level and sport_level.level:
            # 回傳等級的第一個字 (例如 'C(初學者)' -> 'C')
            return sport_level.level[0]
            
        return 'C' # 預設回傳 C
```

---

## 修正二：增加主揪刪除球局的權限保護

原本的刪除 API 並沒有去檢查發送請求的人是否為該球局的「主揪 (Creator)」，這會導致任何登入的用戶只要呼叫 API 都可以刪除別人的球局。我們需要覆寫 `GameMatchViewSet` 的 `destroy` 方法來加入權限驗證。

### 修改目標檔案
`backend/api_v1/views.py`

### 具體程式碼變更

找到 `GameMatchViewSet` 這個類別，在裡面**新增 `destroy` 方法**：

```python
    def destroy(self, request, *args, **kwargs):
        match = self.get_object()
        
        # 檢查發送請求的使用者是否為球局的主揪，或是否為管理員
        if match.creator != request.user and request.user.role != 'admin':
            return Response(
                {"detail": "只有主揪或管理員才能刪除此球局。"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        return super().destroy(request, *args, **kwargs)
```

### 注意事項
* 請確保 `views.py` 最上方有引入 `from rest_framework.response import Response` 與 `from rest_framework import status`（通常已經引入了，確認一下即可）。
* 修改完畢後，前端主揪在點擊「確定取消」時，後端才能正確且安全地刪除球局。

---

## 修正三：在球局 API 中明確提供主揪 ID (`creator_id`)

為了讓前端可以 100% 準確地判斷「當前使用者是否為這個球局的主揪」（以便在首頁顯示莫蘭迪粉色背景與星星標記），我們必須把 `GameMatch` 裡面的 `creator.id` 透過 API 傳給前端。原本前端只能透過名單順序 `participants[0]` 去盲猜，遇到資料庫順序錯亂或非數字轉換時就會失敗。

### 修改目標檔案
`backend/api_v1/serializers.py`

### 具體程式碼變更

找到 `GameMatchSerializer` 這個類別：

1. 在最上方新增一個欄位宣告：
```python
    creator_id = serializers.ReadOnlyField(source='creator.id')
```

2. 並且在 `Meta` 裡的 `fields` 陣列中，加入 `'creator_id'`。

**修改後的 `GameMatchSerializer` 局部會長這樣**：

```python
class GameMatchSerializer(serializers.ModelSerializer):
    # ... 原本的欄位保留
    participants = MatchParticipantUserSerializer(many=True, read_only=True)
    creator_id = serializers.ReadOnlyField(source='creator.id') # <--- 新增這行
    distance_km = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True, required=False)
    # ... 原本的欄位保留

    # ... validate 方法保留

    class Meta:
        model = GameMatch
        fields = [
            'id', 'game_name', 'sport_id', 'sport_name', 'court_id', 'venue_name', 'least_players', 'most_players',
            'current_players', 'target_level', 'booking_date', 'start_time', 'time_slot', 'duration', 'game_note',
            'total_price', 'split_price', 'deposit_required', 'cancel_deadline',
            'weather', 'air_index', 'is_confirmed', 'booking_status',
            'match_status', 'participants', 'creator_id', 'distance_km', 'facilities', # <--- 'creator_id' 加在這裡
            'gender_limit', 'venue_status', 'venue_note'
        ]
        read_only_fields = ('match_status', 'weather', 'air_index', 'is_confirmed', 'facilities', 'time_slot')
```
