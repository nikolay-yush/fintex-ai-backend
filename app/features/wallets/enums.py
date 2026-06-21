from enum import Enum 


class WalletType(str, Enum):
    """Defines the purpose of the wallet."""
    
    SAVINGS = "SAVINGS"
    SPENDINGS = "SPENDINGS"