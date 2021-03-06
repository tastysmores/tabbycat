from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from adjallocation.models import DebateAdjudicator
from results.models import Submission


class AdjudicatorTestScoreHistory(models.Model):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE)
    round = models.ForeignKey('tournaments.Round', models.CASCADE, blank=True, null=True)
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "adjudicator test score histories"

    def __str__(self):
        return "{.name:s} ({:.1f}) in {!s}".format(self.adjudicator, self.score, self.round)


class AdjudicatorFeedbackAnswer(models.Model):
    question = models.ForeignKey('AdjudicatorFeedbackQuestion', models.CASCADE)
    feedback = models.ForeignKey('AdjudicatorFeedback', models.CASCADE)

    class Meta:
        abstract = True
        unique_together = [('question', 'feedback')]


class AdjudicatorFeedbackBooleanAnswer(AdjudicatorFeedbackAnswer):
    # Note: by convention, if no answer is chosen for a boolean answer, an
    # instance of this object should not be created. This way, there is no need
    # for a NullBooleanField.
    answer = models.BooleanField()


class AdjudicatorFeedbackIntegerAnswer(AdjudicatorFeedbackAnswer):
    answer = models.IntegerField()


class AdjudicatorFeedbackFloatAnswer(AdjudicatorFeedbackAnswer):
    answer = models.FloatField()


class AdjudicatorFeedbackStringAnswer(AdjudicatorFeedbackAnswer):
    answer = models.TextField()


class AdjudicatorFeedbackQuestion(models.Model):
    # When adding or changing an answer type, here are the other places you need
    # to edit:
    #   - forms.py : BaseFeedbackForm._make_question_field()
    #   - importer/anorak.py : AnorakTournamentDataImporter.FEEDBACK_ANSWER_TYPES

    ANSWER_TYPE_BOOLEAN_CHECKBOX = 'bc'
    ANSWER_TYPE_BOOLEAN_SELECT = 'bs'
    ANSWER_TYPE_INTEGER_TEXTBOX = 'i'
    ANSWER_TYPE_INTEGER_SCALE = 'is'
    ANSWER_TYPE_FLOAT = 'f'
    ANSWER_TYPE_TEXT = 't'
    ANSWER_TYPE_LONGTEXT = 'tl'
    ANSWER_TYPE_SINGLE_SELECT = 'ss'
    ANSWER_TYPE_MULTIPLE_SELECT = 'ms'
    ANSWER_TYPE_CHOICES = ((ANSWER_TYPE_BOOLEAN_CHECKBOX, 'checkbox'),
                           (ANSWER_TYPE_BOOLEAN_SELECT, 'yes/no (dropdown)'),
                           (ANSWER_TYPE_INTEGER_TEXTBOX, 'integer (textbox)'),
                           (ANSWER_TYPE_INTEGER_SCALE, 'integer scale'),
                           (ANSWER_TYPE_FLOAT, 'float'),
                           (ANSWER_TYPE_TEXT, 'text'),
                           (ANSWER_TYPE_LONGTEXT, 'long text'),
                           (ANSWER_TYPE_SINGLE_SELECT, 'select one'),
                           (ANSWER_TYPE_MULTIPLE_SELECT, 'select multiple'), )
    ANSWER_TYPE_CLASSES = {
        ANSWER_TYPE_BOOLEAN_CHECKBOX: AdjudicatorFeedbackBooleanAnswer,
        ANSWER_TYPE_BOOLEAN_SELECT: AdjudicatorFeedbackBooleanAnswer,
        ANSWER_TYPE_INTEGER_TEXTBOX: AdjudicatorFeedbackIntegerAnswer,
        ANSWER_TYPE_INTEGER_SCALE: AdjudicatorFeedbackIntegerAnswer,
        ANSWER_TYPE_FLOAT: AdjudicatorFeedbackFloatAnswer,
        ANSWER_TYPE_TEXT: AdjudicatorFeedbackStringAnswer,
        ANSWER_TYPE_LONGTEXT: AdjudicatorFeedbackStringAnswer,
        ANSWER_TYPE_SINGLE_SELECT: AdjudicatorFeedbackStringAnswer,
        ANSWER_TYPE_MULTIPLE_SELECT: AdjudicatorFeedbackStringAnswer,
    }
    ANSWER_TYPE_CLASSES_REVERSE = {
        AdjudicatorFeedbackStringAnswer: [ANSWER_TYPE_TEXT,
                                          ANSWER_TYPE_LONGTEXT,
                                          ANSWER_TYPE_SINGLE_SELECT,
                                          ANSWER_TYPE_MULTIPLE_SELECT],
        AdjudicatorFeedbackIntegerAnswer:
        [ANSWER_TYPE_INTEGER_SCALE, ANSWER_TYPE_INTEGER_TEXTBOX],
        AdjudicatorFeedbackFloatAnswer: [ANSWER_TYPE_FLOAT],
        AdjudicatorFeedbackBooleanAnswer:
        [ANSWER_TYPE_BOOLEAN_SELECT, ANSWER_TYPE_BOOLEAN_CHECKBOX],
    }
    CHOICE_SEPARATOR = "//"

    tournament = models.ForeignKey('tournaments.Tournament', models.CASCADE)
    seq = models.IntegerField(help_text="The order in which questions are displayed")
    text = models.CharField(max_length=255,
        help_text="The question displayed to participants, e.g., \"Did you agree with the decision?\"")
    name = models.CharField(max_length=30,
        help_text="A short name for the question, e.g., \"Agree with decision\"")
    reference = models.SlugField(
        help_text="Code-compatible reference, e.g., \"agree_with_decision\"")

    from_adj = models.BooleanField(help_text="Adjudicators should be asked this question (about other adjudicators)")
    from_team = models.BooleanField(help_text="Teams should be asked this question")

    answer_type = models.CharField(max_length=2, choices=ANSWER_TYPE_CHOICES)
    required = models.BooleanField(default=True,
        help_text="Whether participants are required to fill out this field")
    min_value = models.FloatField(blank=True, null=True,
        help_text="Minimum allowed value for numeric fields (ignored for text or boolean fields)")
    max_value = models.FloatField(blank=True, null=True,
        help_text="Maximum allowed value for numeric fields (ignored for text or boolean fields)")
    choices = models.CharField(max_length=500, blank=True,
        help_text="Permissible choices for select one/multiple fields, separated by %r (ignored for other fields)" % CHOICE_SEPARATOR)

    class Meta:
        unique_together = [('tournament', 'reference'), ('tournament', 'seq')]

    def __str__(self):
        return self.reference

    @property
    def answer_set(self):
        return self.answer_type_class.objects.filter(question=self)

    @property
    def answer_type_class(self):
        return self.ANSWER_TYPE_CLASSES[self.answer_type]

    @property
    def choices_for_field(self):
        return tuple((x, x) for x in self.choices.split(self.CHOICE_SEPARATOR))

    @property
    def choices_for_number_scale(self):
        step = max((int(self.max_value) - int(self.min_value)) / 10, 1)
        options = list(range(int(self.min_value), int(self.max_value + 1), int(step)))
        return options


class AdjudicatorFeedback(Submission):
    adjudicator = models.ForeignKey('participants.Adjudicator', models.CASCADE, db_index=True)
    score = models.FloatField()

    source_adjudicator = models.ForeignKey('adjallocation.DebateAdjudicator', models.CASCADE, blank=True, null=True)
    source_team = models.ForeignKey('draw.DebateTeam', models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = [('adjudicator', 'source_adjudicator', 'source_team',
                            'version')]

    def __str__(self):
        return "Feedback from {source} on {adj} submitted at {time} (version {version})".format(
            source=self.source,
            adj=self.adjudicator.name,
            version=self.version,
            time=('<unknown>' if self.timestamp is None else str(
                self.timestamp.isoformat())))

    @cached_property
    def source(self):
        if self.source_adjudicator:
            return self.source_adjudicator.adjudicator.name
        if self.source_team:
            return self.source_team.team.short_name

    @cached_property
    def debate(self):
        if self.source_adjudicator:
            return self.source_adjudicator.debate
        if self.source_team:
            return self.source_team.debate

    @cached_property
    def debate_adjudicator(self):
        try:
            return self.adjudicator.debateadjudicator_set.get(
                debate=self.debate)
        except DebateAdjudicator.DoesNotExist:
            return None

    @property
    def round(self):
        return self.debate.round

    @cached_property
    def feedback_weight(self):
        if self.round:
            return self.round.feedback_weight
        return 1

    def clean(self):
        if not (self.source_adjudicator or self.source_team):
            raise ValidationError(
                "Either the source adjudicator or source team wasn't specified.")
        if self.source_adjudicator and self.source_team:
            raise ValidationError(
                "There was both a source adjudicator and a source team.")
        if self.adjudicator not in self.debate.adjudicators:
            raise ValidationError("Adjudicator did not see this debate.")
        return super(AdjudicatorFeedback, self).clean()
