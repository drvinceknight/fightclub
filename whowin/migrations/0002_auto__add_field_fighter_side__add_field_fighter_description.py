# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Fighter.side'
        db.add_column(u'whowin_fighter', 'side',
                      self.gf('django.db.models.fields.CharField')(default='N', max_length=1),
                      keep_default=False)

        # Adding field 'Fighter.description'
        db.add_column(u'whowin_fighter', 'description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Fighter.side'
        db.delete_column(u'whowin_fighter', 'side')

        # Deleting field 'Fighter.description'
        db.delete_column(u'whowin_fighter', 'description')


    models = {
        u'whowin.fight': {
            'Meta': {'object_name': 'Fight'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fighter_1'", 'to': u"orm['whowin.Fighter']"}),
            'member2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fighter_2'", 'to': u"orm['whowin.Fighter']"})
        },
        u'whowin.fighter': {
            'Meta': {'object_name': 'Fighter'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'fightslost': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fightswon': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rating': ('django.db.models.fields.DecimalField', [], {'default': '1600', 'max_digits': '8', 'decimal_places': '2'}),
            'side': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': '0', 'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['whowin']