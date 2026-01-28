"""Service for loading, saving, and managing research protocols.

Handles YAML-based protocol storage with type discrimination
and versioning support.
"""

from pathlib import Path
from typing import Union
import yaml

from models.enums import ResearchMethodType
from models.protocol import (
    ResearchProtocol,
    SurveyProtocol,
    InterviewProtocol,
    FocusGroupProtocol,
)
from models.survey import Survey, SurveyQuestion
from models.interview import (
    InterviewGuide,
    InterviewSection,
    InterviewQuestion,
    InterviewProbe,
)
from models.focus_group import FocusGroup, FocusGroupConfig


class ProtocolLoaderError(Exception):
    """Exception raised for protocol loading errors."""

    pass


ProtocolType = Union[SurveyProtocol, InterviewProtocol, FocusGroupProtocol]


class ProtocolLoader:
    """Loads and manages research protocols from YAML files.

    Supports loading by ID, listing protocols, saving new protocols,
    and protocol versioning with copy-on-write semantics.
    """

    # Default protocols directory relative to project root
    DEFAULT_PROTOCOLS_DIR = Path("protocols")

    # Type to subdirectory mapping
    TYPE_DIRS = {
        ResearchMethodType.SURVEY: "surveys",
        ResearchMethodType.INTERVIEW: "interviews",
        ResearchMethodType.FOCUS_GROUP: "focus-groups",
    }

    def __init__(self, protocols_dir: Path | None = None):
        """Initialize the protocol loader.

        Args:
            protocols_dir: Optional path to protocols directory.
                          Defaults to 'protocols/' in project root.
        """
        self.protocols_dir = protocols_dir or self.DEFAULT_PROTOCOLS_DIR

    def load_by_id(self, protocol_id: str) -> ProtocolType:
        """Load a protocol by its ID.

        Searches all protocol type directories for a matching ID.

        Args:
            protocol_id: The protocol identifier to load.

        Returns:
            The loaded protocol (typed based on protocol type).

        Raises:
            ProtocolLoaderError: If protocol not found or invalid.
        """
        # Search in all type directories
        for method_type, subdir in self.TYPE_DIRS.items():
            dir_path = self.protocols_dir / subdir
            if not dir_path.exists():
                continue

            # Check for matching file
            yaml_path = dir_path / f"{protocol_id}.yaml"
            if yaml_path.exists():
                return self._load_from_file(yaml_path, method_type)

            # Also check versioned files
            for file_path in dir_path.glob(f"{protocol_id}*.yaml"):
                if file_path.stem == protocol_id or file_path.stem.startswith(
                    f"{protocol_id}-v"
                ):
                    return self._load_from_file(file_path, method_type)

        raise ProtocolLoaderError(f"Protocol not found: {protocol_id}")

    def list_protocols(
        self, method_type: ResearchMethodType | None = None
    ) -> list[ResearchProtocol]:
        """List all available protocols.

        Args:
            method_type: Optional filter by research method type.

        Returns:
            List of protocol objects (base class for listing).
        """
        protocols = []

        if method_type:
            types_to_check = [method_type]
        else:
            types_to_check = list(self.TYPE_DIRS.keys())

        for mt in types_to_check:
            subdir = self.TYPE_DIRS[mt]
            dir_path = self.protocols_dir / subdir

            if not dir_path.exists():
                continue

            for yaml_path in dir_path.glob("*.yaml"):
                try:
                    protocol = self._load_from_file(yaml_path, mt)
                    protocols.append(protocol)
                except (ProtocolLoaderError, ValueError, yaml.YAMLError):
                    # Skip invalid files
                    continue

        return protocols

    def save_protocol(self, protocol: ProtocolType) -> Path:
        """Save a protocol to disk.

        Implements copy-on-write versioning: if a protocol with the same ID
        but different version exists, creates a new versioned file.

        Args:
            protocol: The protocol to save.

        Returns:
            Path to the saved file.

        Raises:
            ProtocolLoaderError: If save fails.
        """
        # Determine subdirectory based on protocol type
        subdir = self.TYPE_DIRS.get(protocol.type)
        if not subdir:
            raise ProtocolLoaderError(f"Unknown protocol type: {protocol.type}")

        dir_path = self.protocols_dir / subdir
        dir_path.mkdir(parents=True, exist_ok=True)

        # Check for existing protocol with same ID
        existing_path = dir_path / f"{protocol.id}.yaml"

        if existing_path.exists():
            # Load existing to check version
            try:
                existing = self._load_from_file(existing_path, protocol.type)
                if existing.version == protocol.version:
                    # Same version - overwrite
                    file_path = existing_path
                else:
                    # Different version - create versioned file
                    file_path = dir_path / f"{protocol.id}-v{protocol.version}.yaml"
            except (ProtocolLoaderError, ValueError):
                # Existing file invalid, overwrite
                file_path = existing_path
        else:
            file_path = existing_path

        # Serialize and save
        yaml_content = self._serialize_protocol(protocol)
        file_path.write_text(yaml_content)

        return file_path

    def delete_protocol(self, protocol_id: str) -> None:
        """Delete a protocol by ID.

        Args:
            protocol_id: The protocol identifier to delete.

        Raises:
            ProtocolLoaderError: If protocol not found.
        """
        # Find the file
        for method_type, subdir in self.TYPE_DIRS.items():
            dir_path = self.protocols_dir / subdir
            if not dir_path.exists():
                continue

            yaml_path = dir_path / f"{protocol_id}.yaml"
            if yaml_path.exists():
                yaml_path.unlink()
                return

            # Check versioned files
            for file_path in dir_path.glob(f"{protocol_id}*.yaml"):
                if file_path.stem == protocol_id or file_path.stem.startswith(
                    f"{protocol_id}-v"
                ):
                    file_path.unlink()
                    return

        raise ProtocolLoaderError(f"Protocol not found: {protocol_id}")

    def _load_from_file(
        self, file_path: Path, method_type: ResearchMethodType
    ) -> ProtocolType:
        """Load a protocol from a YAML file.

        Args:
            file_path: Path to the YAML file.
            method_type: Expected protocol type.

        Returns:
            Typed protocol object.

        Raises:
            ProtocolLoaderError: If file is invalid.
        """
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as e:
            raise ProtocolLoaderError(f"Failed to load {file_path}: {e}")

        if not data or "protocol" not in data:
            raise ProtocolLoaderError(f"Invalid protocol file: {file_path}")

        protocol_data = data["protocol"]

        # Validate type matches
        file_type = protocol_data.get("type", "").lower()
        if file_type == "focus_group":
            file_type = ResearchMethodType.FOCUS_GROUP
        else:
            try:
                file_type = ResearchMethodType(file_type)
            except ValueError:
                raise ProtocolLoaderError(f"Unknown protocol type: {file_type}")

        # Parse based on type
        if file_type == ResearchMethodType.SURVEY:
            return self._parse_survey_protocol(data)
        elif file_type == ResearchMethodType.INTERVIEW:
            return self._parse_interview_protocol(data)
        elif file_type == ResearchMethodType.FOCUS_GROUP:
            return self._parse_focus_group_protocol(data)
        else:
            raise ProtocolLoaderError(f"Unsupported protocol type: {file_type}")

    def _parse_survey_protocol(self, data: dict) -> SurveyProtocol:
        """Parse survey protocol from YAML data."""
        protocol_data = data["protocol"]
        survey_data = data.get("survey", {})

        # Parse questions
        questions = []
        for q in survey_data.get("questions", []):
            questions.append(SurveyQuestion(**q))

        survey = Survey(
            id=survey_data.get("id", protocol_data["id"]),
            version=survey_data.get("version", protocol_data["version"]),
            name=survey_data.get("name", protocol_data["name"]),
            description=survey_data.get("description"),
            questions=questions,
        )

        return SurveyProtocol(
            id=protocol_data["id"],
            version=protocol_data["version"],
            name=protocol_data["name"],
            description=protocol_data.get("description"),
            tags=protocol_data.get("tags", []),
            survey=survey,
        )

    def _parse_interview_protocol(self, data: dict) -> InterviewProtocol:
        """Parse interview protocol from YAML data."""
        protocol_data = data["protocol"]
        guide_data = data.get("guide", {})

        # Parse sections
        sections = []
        for s in guide_data.get("sections", []):
            # Parse questions in section
            questions = []
            for q in s.get("questions", []):
                # Parse probes
                probes = [InterviewProbe(**p) for p in q.get("probes", [])]
                questions.append(
                    InterviewQuestion(
                        id=q["id"],
                        text=q["text"],
                        probes=probes,
                        allow_followups=q.get("allow_followups", True),
                        max_followup_depth=q.get("max_followup_depth", 3),
                    )
                )

            sections.append(
                InterviewSection(
                    id=s["id"],
                    name=s["name"],
                    description=s.get("description"),
                    questions=questions,
                    transition_prompt=s.get("transition_prompt"),
                )
            )

        guide = InterviewGuide(
            id=guide_data.get("id", protocol_data["id"]),
            version=guide_data.get("version", protocol_data["version"]),
            name=guide_data.get("name", protocol_data["name"]),
            topic=guide_data.get("topic", ""),
            description=guide_data.get("description"),
            sections=sections,
            min_response_length=guide_data.get("min_response_length", 50),
            default_max_followups=guide_data.get("default_max_followups", 3),
        )

        return InterviewProtocol(
            id=protocol_data["id"],
            version=protocol_data["version"],
            name=protocol_data["name"],
            description=protocol_data.get("description"),
            tags=protocol_data.get("tags", []),
            guide=guide,
        )

    def _parse_focus_group_protocol(self, data: dict) -> FocusGroupProtocol:
        """Parse focus group protocol from YAML data."""
        protocol_data = data["protocol"]
        fg_data = data.get("focus_group", {})

        # Parse config
        config_data = fg_data.get("config", {})
        config = FocusGroupConfig(
            max_rounds=config_data.get("max_rounds", 3),
            turns_per_round=config_data.get("turns_per_round", 6),
            moderator_prompts_enabled=config_data.get("moderator_prompts_enabled", True),
            allow_cross_references=config_data.get("allow_cross_references", True),
        )

        focus_group = FocusGroup(
            id=fg_data.get("id", protocol_data["id"]),
            version=fg_data.get("version", protocol_data["version"]),
            name=fg_data.get("name", protocol_data["name"]),
            description=fg_data.get("description"),
            persona_ids=fg_data.get("persona_ids", []),
            discussion_topics=fg_data.get("discussion_topics", []),
            config=config,
        )

        return FocusGroupProtocol(
            id=protocol_data["id"],
            version=protocol_data["version"],
            name=protocol_data["name"],
            description=protocol_data.get("description"),
            tags=protocol_data.get("tags", []),
            focus_group=focus_group,
        )

    def _serialize_protocol(self, protocol: ProtocolType) -> str:
        """Serialize a protocol to YAML string.

        Args:
            protocol: The protocol to serialize.

        Returns:
            YAML string representation.
        """
        data = {
            "protocol": {
                "id": protocol.id,
                "version": protocol.version,
                "type": protocol.type.value,
                "name": protocol.name,
                "description": protocol.description,
                "tags": protocol.tags,
            }
        }

        if isinstance(protocol, SurveyProtocol):
            survey = protocol.survey
            data["survey"] = {
                "id": survey.id,
                "version": survey.version,
                "name": survey.name,
                "description": survey.description,
                "questions": [
                    {
                        "id": q.id,
                        "text": q.text,
                        "type": q.type.value,
                        "required": q.required,
                        **(
                            {"scale_min": q.scale_min, "scale_max": q.scale_max}
                            if q.scale_min is not None
                            else {}
                        ),
                        **({"scale_labels": q.scale_labels} if q.scale_labels else {}),
                        **({"options": q.options} if q.options else {}),
                    }
                    for q in survey.questions
                ],
            }
        elif isinstance(protocol, InterviewProtocol):
            guide = protocol.guide
            data["guide"] = {
                "id": guide.id,
                "version": guide.version,
                "name": guide.name,
                "topic": guide.topic,
                "description": guide.description,
                "min_response_length": guide.min_response_length,
                "default_max_followups": guide.default_max_followups,
                "sections": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "description": s.description,
                        "transition_prompt": s.transition_prompt,
                        "questions": [
                            {
                                "id": q.id,
                                "text": q.text,
                                "allow_followups": q.allow_followups,
                                "max_followup_depth": q.max_followup_depth,
                                "probes": [
                                    {
                                        "type": p.type.value,
                                        "trigger": p.trigger,
                                        "question_template": p.question_template,
                                    }
                                    for p in q.probes
                                ],
                            }
                            for q in s.questions
                        ],
                    }
                    for s in guide.sections
                ],
            }
        elif isinstance(protocol, FocusGroupProtocol):
            fg = protocol.focus_group
            data["focus_group"] = {
                "id": fg.id,
                "version": fg.version,
                "name": fg.name,
                "description": fg.description,
                "persona_ids": fg.persona_ids,
                "discussion_topics": fg.discussion_topics,
                "config": {
                    "max_rounds": fg.config.max_rounds,
                    "turns_per_round": fg.config.turns_per_round,
                    "moderator_prompts_enabled": fg.config.moderator_prompts_enabled,
                    "allow_cross_references": fg.config.allow_cross_references,
                },
            }

        return yaml.dump(data, default_flow_style=False, sort_keys=False)
