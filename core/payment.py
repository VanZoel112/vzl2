"""
Vzoel Fox's Lutpan - Payment System Manager
QR code and payment information management

Features:
- Payment info storage
- QR code file_id management
- Quick payment display
- Database persistence

Author: Vzoel Fox's
Contact: @VZLfxs
"""

import json
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PaymentManager:
    """
    Payment information manager for Vzoel Fox's Lutpan
    Handles payment gateway info and QR codes
    """

    def __init__(self, db_path: str = "database/payment.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> Dict:
        """Load payment data from JSON file"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Load error: {e}")
                return {}
        return {}

    def _save(self):
        """Save payment data to JSON file"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Save error: {e}")

    def set_payment_info(self, info: Dict) -> bool:
        """
        Set payment gateway information

        Args:
            info: Dict with payment details

        Returns:
            True if saved successfully
        """
        try:
            if 'payment' not in self.data:
                self.data['payment'] = {}

            self.data['payment'].update(info)
            self._save()
            logger.info("Payment info saved")
            return True

        except Exception as e:
            logger.error(f"Set payment info error: {e}")
            return False

    def get_payment_info(self) -> Optional[Dict]:
        """
        Get stored payment information

        Returns:
            Dict with payment info or None
        """
        return self.data.get('payment')

    def set_qr_code(self, file_id: str, description: Optional[str] = None) -> bool:
        """
        Store QR code file_id

        Args:
            file_id: Telegram file_id for QR image
            description: Optional description

        Returns:
            True if saved successfully
        """
        try:
            if 'qr_codes' not in self.data:
                self.data['qr_codes'] = []

            qr_entry = {
                'file_id': file_id,
                'description': description or 'Payment QR Code',
                'is_primary': len(self.data['qr_codes']) == 0
            }

            self.data['qr_codes'].append(qr_entry)
            self._save()
            logger.info(f"QR code saved: {file_id}")
            return True

        except Exception as e:
            logger.error(f"Set QR code error: {e}")
            return False

    def get_qr_code(self, index: int = 0) -> Optional[Dict]:
        """
        Get stored QR code info

        Args:
            index: QR code index (0 for primary)

        Returns:
            Dict with QR info or None
        """
        qr_codes = self.data.get('qr_codes', [])
        if qr_codes and 0 <= index < len(qr_codes):
            return qr_codes[index]
        return None

    def get_primary_qr(self) -> Optional[Dict]:
        """Get primary QR code"""
        qr_codes = self.data.get('qr_codes', [])
        for qr in qr_codes:
            if qr.get('is_primary'):
                return qr
        return qr_codes[0] if qr_codes else None

    def list_qr_codes(self) -> list:
        """List all stored QR codes"""
        return self.data.get('qr_codes', [])

    def remove_qr_code(self, index: int) -> bool:
        """
        Remove QR code by index

        Args:
            index: QR code index

        Returns:
            True if removed successfully
        """
        try:
            qr_codes = self.data.get('qr_codes', [])
            if 0 <= index < len(qr_codes):
                qr_codes.pop(index)
                self.data['qr_codes'] = qr_codes
                self._save()
                logger.info(f"QR code {index} removed")
                return True
            return False

        except Exception as e:
            logger.error(f"Remove QR error: {e}")
            return False

    def set_primary_qr(self, index: int) -> bool:
        """
        Set QR code as primary

        Args:
            index: QR code index

        Returns:
            True if set successfully
        """
        try:
            qr_codes = self.data.get('qr_codes', [])
            if 0 <= index < len(qr_codes):
                # Remove primary flag from all
                for qr in qr_codes:
                    qr['is_primary'] = False

                # Set new primary
                qr_codes[index]['is_primary'] = True
                self.data['qr_codes'] = qr_codes
                self._save()
                logger.info(f"QR code {index} set as primary")
                return True
            return False

        except Exception as e:
            logger.error(f"Set primary QR error: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get payment system statistics"""
        return {
            'has_payment_info': bool(self.data.get('payment')),
            'qr_codes_count': len(self.data.get('qr_codes', [])),
            'has_primary_qr': bool(self.get_primary_qr())
        }

    def clear_all(self) -> bool:
        """Clear all payment data"""
        try:
            self.data = {}
            self._save()
            logger.info("Payment data cleared")
            return True
        except Exception as e:
            logger.error(f"Clear error: {e}")
            return False
