from data.db.connection.session import get_session
from domain.services.auth_service import AuthService
from domain.services.balance_service import BalanceService
from domain.services.deal_service import DealService
from domain.services.info_service import InfoService
from domain.services.transaction_service import TransactionService
from data.adapters.user_repo import UserRepo
from data.adapters.deal_repo import DealRepo
from data.adapters.transaction_repo import TransactionRepo
from data.adapters.item_repo import ItemRepo
from settings import Settings

import aioinject

container = aioinject.Container()
container.register(aioinject.Object(Settings()))
container.register(aioinject.Scoped(get_session))
container.register(aioinject.Scoped(DealRepo))
container.register(aioinject.Scoped(UserRepo))
container.register(aioinject.Scoped(TransactionRepo))
container.register(aioinject.Scoped(ItemRepo))
container.register(aioinject.Scoped(AuthService))
container.register(aioinject.Scoped(BalanceService))
container.register(aioinject.Scoped(DealService))
container.register(aioinject.Scoped(InfoService))
container.register(aioinject.Scoped(TransactionService))
