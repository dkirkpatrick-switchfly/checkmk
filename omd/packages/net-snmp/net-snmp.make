NET_SNMP := net-snmp
NET_SNMP_DIR := $(NET_SNMP)

NET_SNMP_BUILD := $(BUILD_HELPER_DIR)/$(NET_SNMP_DIR)-build
NET_SNMP_INTERMEDIATE_INSTALL := $(BUILD_HELPER_DIR)/$(NET_SNMP_DIR)-install-intermediate
NET_SNMP_INSTALL := $(BUILD_HELPER_DIR)/$(NET_SNMP_DIR)-install

NET_SNMP_INSTALL_DIR := $(INTERMEDIATE_INSTALL_BASE)/$(NET_SNMP_DIR)

$(NET_SNMP_BUILD):
# Skip Perl-Modules because of build errors when MIB loading is disabled.
# Skip Python binding because we need to use our own python, see install target.
	$(BAZEL_BUILD) @$(NET_SNMP)//:$(NET_SNMP)

$(NET_SNMP_INTERMEDIATE_INSTALL): $(NET_SNMP_BUILD)
	$(RSYNC) --chmod=u+w $(BAZEL_BIN_EXT)/$(NET_SNMP)/$(NET_SNMP)/ $(NET_SNMP_INSTALL_DIR)

$(NET_SNMP_INSTALL): $(NET_SNMP_INTERMEDIATE_INSTALL)
	$(RSYNC) $(NET_SNMP_INSTALL_DIR)/ $(DESTDIR)$(OMD_ROOT)/
