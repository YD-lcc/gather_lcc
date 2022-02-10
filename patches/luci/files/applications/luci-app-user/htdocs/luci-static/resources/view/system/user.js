'use strict';
'require view';
'require dom';
'require fs';
'require ui';
'require uci';
'require form';

return view.extend({
	checkPassword: function(section_id, value) {
		var strength = document.querySelector('.cbi-map-descr'),
			strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g"),
			mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g"),
			enoughRegex = new RegExp("(?=.{6,}).*", "g");
		if (strength && value.length) {
			if (false == enoughRegex.test(value)) {
				strength.innerHTML = '<span style="text-align:center">%s: <span style="color:red">%s</span></span>'.format(_('Password strength'), _('More Characters'));
				return _('More Characters');
            }
			else if (strongRegex.test(value))
				strength.innerHTML = '%s: <span style="color:green">%s</span>'.format(_('Password strength'), _('Strong'));
			else if (mediumRegex.test(value))
				strength.innerHTML = '%s: <span style="color:orange">%s</span>'.format(_('Password strength'), _('Medium'));
			else
				strength.innerHTML = '%s: <span style="color:red">%s</span>'.format(_('Password strength'), _('Weak'));
		}
		return true;
	},
	render: function() {
		var m, s, o;
		m = new form.Map('rpcd', _('Router Password'), _('Changes the administrator password for accessing the device'));
		m.readonly = !L.hasViewPermission();
		s = m.section(form.NamedSection, '@login[1]');
		o = s.option(form.Value, 'username', _('Login name'));
		o.rmempty = false;
		s = m.section(form.NamedSection, '@login[1]');
		o = s.option(form.Value, 'password', _('Password'));
		o.password = true;
		o.validate = this.checkPassword;
		o.write = function(section_id, value) {
			return fs.exec('/usr/sbin/uhttpd', ['-m', value])
                .then(function(res) {
					if (res.code == 0 && res.stdout) {
                        ui.addNotification(null, E('p', _('Use encrypted password hash')), 'info');
						uci.set('rpcd', section_id, 'password', res.stdout.trim());
						uci.set('rpcd', section_id, 'login');
                    }
                    else
                        throw new Error(res.stderr);
                }).catch(function(err) {
                    throw new Error(_('Unable to encrypt plaintext password: %s').format(err.message));
                });
			uci.set('rpcd', section_id, 'password', value);
			uci.set('rpcd', section_id, 'login');
		};
		o = s.option(form.Value, '',_('Confirmation'));
		o.password = true;
		o.validate = function(section_id, value) {
            var variant = this.map.lookupOption('password', section_id)[0];
            return variant.formvalue(section_id)==value ? true : _('Given password confirmation did not match, password not changed!');
		};
		o.renderWidget = function() {
			var node = form.Value.prototype.renderWidget.apply(this, arguments);
			node.querySelector('input')
				.addEventListener('keydown', function(ev) {
					if (ev.keyCode == 13 && !ev.currentTarget.classList.contains('cbi-input-invalid'))
						document.querySelector('.cbi-button-save')
						.click();
				});
			return node;
		};
		o.write = function() {};
		return m.render();
	}
});