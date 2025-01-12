from django.db import models
from simple_history.models import HistoricalRecords

class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "countries"

class MitreTactic(models.Model):
    mitre_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return '{} - {}'.format(self.mitre_id, self.name)
    
    class Meta:
        ordering = ['mitre_id']

class MitreTechnique(models.Model):
    mitre_id = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=150)
    is_subtechnique = models.BooleanField() 
    mitre_technique = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    mitre_tactic = models.ManyToManyField(MitreTactic)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return '{} - {}'.format(self.mitre_id, self.name)
    
    class Meta:
        ordering = ['mitre_id']

class ThreatName(models.Model):
    name = models.CharField(max_length=100, verbose_name="Threat name or software", unique=True)
    aka_name = models.CharField(max_length=500, blank=True, help_text="Also known as, separator: comma")
    references = models.TextField(blank=True, help_text="List of sources, one per line")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ThreatActor(models.Model):
    name = models.CharField(max_length=100, verbose_name="Threat actor", unique=True)
    aka_name = models.CharField(max_length=500, blank=True, help_text="Also known as, separator: comma")
    source_country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    references = models.TextField(blank=True, help_text="List of sources, one per line")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class TargetOs(models.Model):
    name = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "target OS"

class Vulnerability(models.Model):
    name = models.CharField(max_length=20, verbose_name="format: CVE-XXXX-XXXX", unique=True)
    base_score = models.FloatField()
    description = models.TextField(blank=True)
    references = models.TextField(blank=True, help_text="List of sources, one per line")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "vulnerabilities"

class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Query(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('DIST', 'Production'),
    ]
    CONFIDENCE_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    RELEVANCE_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, help_text="Description, Markdown syntax")
    notes = models.TextField(blank=True, help_text="Threat hunting notes, Markdown syntax")
    pub_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    pub_status = models.CharField(max_length=5, choices=STATUS_CHOICES, default='DRAFT')
    confidence = models.IntegerField(choices=CONFIDENCE_CHOICES, default=1)
    relevance = models.IntegerField(choices=RELEVANCE_CHOICES, default=1)
    weighted_relevance = models.GeneratedField(
        expression=models.F("relevance") * models.F("confidence")/4,
        output_field=models.FloatField(),
        db_persist=False
    )
    query = models.TextField()
    columns = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    mitre_techniques = models.ManyToManyField(MitreTechnique, blank=True)
    threats = models.ManyToManyField(ThreatName, blank=True)
    actors = models.ManyToManyField(ThreatActor, blank=True)
    target_os = models.ManyToManyField(TargetOs, blank=True)
    vulnerabilities = models.ManyToManyField(Vulnerability, blank=True)
    emulation_validation = models.TextField(blank=True, help_text="Emulation and validation, Markdown syntax")
    references = models.TextField(blank=True, help_text="List of sources, one per line")
    star_rule = models.BooleanField(default=False)
    run_daily = models.BooleanField(default=True)
    dynamic_query = models.BooleanField(default=False)
    anomaly_threshold_count = models.IntegerField(default=2, help_text="Value range from 0 to 3. The higher the less sensitive")
    anomaly_threshold_endpoints = models.IntegerField(default=2, help_text="Value range from 0 to 3. The higher the less sensitive")
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "queries"

class Campaign(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(blank=True, null=True)
    nb_queries = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
   
class Snapshot(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    date = models.DateField()
    hits_count = models.IntegerField(default=0)
    hits_endpoints = models.IntegerField(default=0)
    hits_c1 = models.IntegerField(default=0)
    hits_c2 = models.IntegerField(default=0)
    hits_c3 = models.IntegerField(default=0)
    zscore_count = models.FloatField(default=0)
    zscore_endpoints = models.FloatField(default=0)
    anomaly_alert_count = models.BooleanField(default=False)
    anomaly_alert_endpoints = models.BooleanField(default=False)
    
    def __str__(self):
        return '{} - {}'.format(self.date, self.query.name)

class Endpoint(models.Model):
    hostname = models.CharField(max_length=253)
    site = models.CharField(max_length=253, blank=True)
    snapshot = models.ForeignKey(Snapshot, on_delete=models.CASCADE)
    storylineid = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return '{} - {} - {}'.format(self.snapshot.date, self.hostname, self.snapshot.query.name)

class CeleryStatus(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField()

    def __str__(self):
        return self.query.name
    
    class Meta:
        verbose_name_plural = "celery status"
