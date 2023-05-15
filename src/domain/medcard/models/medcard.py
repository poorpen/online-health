from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from src.domain.common.models.aggregate import AggregateRoot

from src.domain.medcard.models.doctor_note import DoctorNote
from src.domain.medcard.models.anamesis_vitae_point import AnamnesisVitaePoint
from src.domain.medcard.value_objects.doctor_note import AnamnesisMorbi, Diagnosis, TreatmentPlan
from src.domain.medcard.value_objects.anamnesis_vitae_point import CategoryID, AnswerID
from src.domain.medcard.value_objects.anthropometry import Height, Weight
from src.domain.medcard.exceptions.anamnesis_vitae_point import AnamnesisVitaePointNotExist


@dataclass
class MedCard(AggregateRoot):
    uuid: UUID
    patient_uuid: UUID
    height: Height
    weight: Weight
    date_of_birth: datetime
    anamnesis_vitae: List[AnamnesisVitaePoint]

    def add_doctor_note(
            self,
            doctor_uuid: UUID,
            anamnesis_morbi: AnamnesisMorbi,
            diagnosis: Diagnosis,
            treatment_plan: TreatmentPlan
    ) -> DoctorNote:
        return DoctorNote(
            uuid=uuid4(),
            medcard_uuid=self.uuid,
            doctor_uuid=doctor_uuid,
            anamnesis_morbi=anamnesis_morbi,
            diagnosis=diagnosis,
            treatment_plan=treatment_plan
        )

    def add_answers__in_anamnesis_vitae(self, answers_ids: List[AnswerID], category_id: CategoryID) -> None:
        anamnesis_vitae_point = self._search_anamnesis_vitae_point(category_id)
        if not anamnesis_vitae_point:
            anamnesis_vitae_point = AnamnesisVitaePoint(medcard_uuid=self.uuid, category_id=category_id)
        anamnesis_vitae_point.add_answer(answers_ids)

    def delete_answers_in_anamnesis_vitae(self, answers_ids: List[AnswerID], category_id: CategoryID) -> None:
        anamnesis_vitae_point = self._search_anamnesis_vitae_point(category_id)
        if not anamnesis_vitae_point:
            raise AnamnesisVitaePointNotExist(category_id)
        anamnesis_vitae_point.delete_answer(answers_ids)

    def edit_anthropometry_data(self, weight: Optional[Weight] = None, height: Optional[Height] = None) -> None:
        if weight:
            self.weight = weight
        if height:
            self.height = height

    def _search_anamnesis_vitae_point(self, category_id: CategoryID) -> AnamnesisVitaePoint | None:
        low = 0
        high = len(self.anamnesis_vitae) - 1
        while low <= high:
            mid = (low + high) // 2
            mid_item: AnamnesisVitaePoint = self.anamnesis_vitae[mid]
            if mid_item.category_id == category_id:
                return mid_item
            elif mid_item.category_id < category_id:
                low = mid + 1
            elif mid_item.category_id > category_id:
                high = mid - 1