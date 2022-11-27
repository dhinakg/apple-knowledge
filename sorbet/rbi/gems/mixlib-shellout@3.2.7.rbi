# typed: true

# DO NOT EDIT MANUALLY
# This is an autogenerated file for types exported from the `mixlib-shellout` gem.
# Please instead update this file by running `bin/tapioca gem mixlib-shellout`.

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:1
module Mixlib; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:2
class Mixlib::ShellOut
  include ::Mixlib::ShellOut::Unix

  # === Arguments:
  # Takes a single command, or a list of command fragments. These are used
  # as arguments to Kernel.exec. See the Kernel.exec documentation for more
  # explanation of how arguments are evaluated. The last argument can be an
  # options Hash.
  # === Options:
  # If the last argument is a Hash, it is removed from the list of args passed
  # to exec and used as an options hash. The following options are available:
  # * +user+: the user the command should run as. if an integer is given, it is
  #   used as a uid. A string is treated as a username and resolved to a uid
  #   with Etc.getpwnam
  # * +group+: the group the command should run as. works similarly to +user+
  # * +cwd+: the directory to chdir to before running the command
  # * +umask+: a umask to set before running the command. If given as an Integer,
  #   be sure to use two leading zeros so it's parsed as Octal. A string will
  #   be treated as an octal integer
  # * +returns+:  one or more Integer values to use as valid exit codes for the
  #   subprocess. This only has an effect if you call +error!+ after
  #   +run_command+.
  # * +environment+: a Hash of environment variables to set before the command
  #   is run.
  # * +timeout+: a Numeric value for the number of seconds to wait on the
  #   child process before raising an Exception. This is calculated as the
  #   total amount of time that ShellOut waited on the child process without
  #   receiving any output (i.e., IO.select returned nil). Default is 600
  #   seconds. Note: the stdlib Timeout library is not used.
  # * +input+: A String of data to be passed to the subcommand. This is
  #   written to the child process' stdin stream before the process is
  #   launched. The child's stdin stream will be a pipe, so the size of input
  #   data should not exceed the system's default pipe capacity (4096 bytes
  #   is a safe value, though on newer Linux systems the capacity is 64k by
  #   default).
  # * +live_stream+: An IO or Logger-like object (must respond to the append
  #   operator +<<+) that will receive data as ShellOut reads it from the
  #   child process. Generally this is used to copy data from the child to
  #   the parent's stdout so that users may observe the progress of
  #   long-running commands.
  # * +login+: Whether to simulate a login (set secondary groups, primary group, environment
  #   variables etc) as done by the OS in an actual login
  # === Examples:
  # Invoke find(1) to search for .rb files:
  #   find = Mixlib::ShellOut.new("find . -name '*.rb'")
  #   find.run_command
  #   # If all went well, the results are on +stdout+
  #   puts find.stdout
  #   # find(1) prints diagnostic info to STDERR:
  #   puts "error messages" + find.stderr
  #   # Raise an exception if it didn't exit with 0
  #   find.error!
  # Run a command as the +www+ user with no extra ENV settings from +/tmp+
  #   cmd = Mixlib::ShellOut.new("apachectl", "start", :user => 'www', :env => nil, :cwd => '/tmp')
  #   cmd.run_command # etc.
  #
  # @return [ShellOut] a new instance of ShellOut
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:169
  def initialize(*command_args); end

  # The command to be executed.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:84
  def command; end

  # Working directory for the subprocess. Normally set via options to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:54
  def cwd; end

  # Working directory for the subprocess. Normally set via options to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:54
  def cwd=(_arg0); end

  # Returns the value of attribute domain.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:41
  def domain; end

  # Sets the attribute domain
  #
  # @param value the value to set the attribute domain to.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:41
  def domain=(_arg0); end

  # Runs windows process with elevated privileges. Required for Powershell commands which need elevated privileges
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:113
  def elevated; end

  # Runs windows process with elevated privileges. Required for Powershell commands which need elevated privileges
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:113
  def elevated=(_arg0); end

  # Environment variables that will be set for the subcommand. Refer to the
  # documentation of new to understand how ShellOut interprets this.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:91
  def environment; end

  # Environment variables that will be set for the subcommand. Refer to the
  # documentation of new to understand how ShellOut interprets this.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:91
  def environment=(_arg0); end

  # If #error? is true, calls +invalid!+, which raises an Exception.
  # === Returns
  # nil::: always returns nil when it does not raise
  # === Raises
  # ::ShellCommandFailed::: via +invalid!+
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:286
  def error!; end

  # Checks the +exitstatus+ against the set of +valid_exit_codes+.
  # === Returns
  # +true+ if +exitstatus+ is not in the list of +valid_exit_codes+, false
  # otherwise.
  #
  # @return [Boolean]
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:277
  def error?; end

  # The amount of time the subcommand took to execute
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:98
  def execution_time; end

  # The exit status of the subprocess. Will be nil if the command is still
  # running or died without setting an exit status (e.g., terminated by
  # `kill -9`).
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:250
  def exitstatus; end

  # Creates a String showing the output of the command, including a banner
  # showing the exact command executed. Used by +invalid!+ to show command
  # results when the command exited with an unexpected status.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:234
  def format_for_exception; end

  # The gid that the subprocess will switch to. If the group attribute is
  # given as a group name, it is converted to a gid by Etc.getgrnam
  # TODO migrate to shellout/unix.rb
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:220
  def gid; end

  # Group the command will run as. Normally set via options passed to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:51
  def group; end

  # Group the command will run as. Normally set via options passed to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:51
  def group=(_arg0); end

  # ShellOut will push data from :input down the stdin of the subprocess.
  # Normally set via options passed to new.
  # Default: nil
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:71
  def input; end

  # ShellOut will push data from :input down the stdin of the subprocess.
  # Normally set via options passed to new.
  # Default: nil
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:71
  def input=(_arg0); end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:303
  def inspect; end

  # Raises a ShellCommandFailed exception, appending the
  # command's stdout, stderr, and exitstatus to the exception message.
  # === Arguments
  # +msg+:  A String to use as the basis of the exception message. The
  # default explanation is very generic, providing a more informative message
  # is highly encouraged.
  # === Raises
  # ShellCommandFailed  always
  #
  # @raise [ShellCommandFailed]
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:298
  def invalid!(msg = T.unsafe(nil)); end

  # When live_stderr is set, the stderr of the subprocess will be copied to it
  # as the subprocess is running.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:66
  def live_stderr; end

  # When live_stderr is set, the stderr of the subprocess will be copied to it
  # as the subprocess is running.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:66
  def live_stderr=(_arg0); end

  # When live_stdout is set, the stdout of the subprocess will be copied to it
  # as the subprocess is running.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:62
  def live_stdout; end

  # When live_stdout is set, the stdout of the subprocess will be copied to it
  # as the subprocess is running.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:62
  def live_stdout=(_arg0); end

  # Returns the stream that both is being used by both live_stdout and live_stderr, or nil
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:191
  def live_stream; end

  # A shortcut for setting both live_stdout and live_stderr, so that both the
  # stdout and stderr from the subprocess will be copied to the same stream as
  # the subprocess is running.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:198
  def live_stream=(stream); end

  # The log level at which ShellOut should log.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:78
  def log_level; end

  # The log level at which ShellOut should log.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:78
  def log_level=(_arg0); end

  # A string which will be prepended to the log message.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:81
  def log_tag; end

  # A string which will be prepended to the log message.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:81
  def log_tag=(_arg0); end

  # If a logger is set, ShellOut will log a message before it executes the
  # command.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:75
  def logger; end

  # If a logger is set, ShellOut will log a message before it executes the
  # command.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:75
  def logger=(_arg0); end

  # Whether to simulate logon as the user. Normally set via options passed to new
  # Always enabled on windows
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:48
  def login; end

  # Whether to simulate logon as the user. Normally set via options passed to new
  # Always enabled on windows
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:48
  def login=(_arg0); end

  # Returns the value of attribute password.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:42
  def password; end

  # Sets the attribute password
  #
  # @param value the value to set the attribute password to.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:42
  def password=(_arg0); end

  # Returns the value of attribute process_status_pipe.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:110
  def process_status_pipe; end

  # Run the command, writing the command's standard out and standard error
  # to +stdout+ and +stderr+, and saving its exit status object to +status+
  # === Returns
  # returns   +self+; +stdout+, +stderr+, +status+, and +exitstatus+ will be
  # populated with results of the command
  # === Raises
  # * Errno::EACCES  when you are not privileged to execute the command
  # * Errno::ENOENT  when the command is not available on the system (or not
  #   in the current $PATH)
  # * CommandTimeout  when the command does not complete
  #   within +timeout+ seconds (default: 600s)
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:265
  def run_command; end

  # Returns the value of attribute sensitive.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:115
  def sensitive; end

  # Sets the attribute sensitive
  #
  # @param value the value to set the attribute sensitive to.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:115
  def sensitive=(_arg0); end

  # A Process::Status (or ducktype) object collected when the subprocess is
  # reaped.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:108
  def status; end

  # Data written to stderr by the subprocess
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:104
  def stderr; end

  # Returns the value of attribute stderr_pipe.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:110
  def stderr_pipe; end

  # Returns the value of attribute stdin_pipe.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:110
  def stdin_pipe; end

  # Data written to stdout by the subprocess
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:101
  def stdout; end

  # Returns the value of attribute stdout_pipe.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:110
  def stdout_pipe; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:227
  def timeout; end

  # The maximum time this command is allowed to run. Usually set via options
  # to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:95
  def timeout=(_arg0); end

  # The uid that the subprocess will switch to. If the user attribute was
  # given as a username, it is converted to a uid by Etc.getpwnam
  # TODO migrate to shellout/unix.rb
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:211
  def uid; end

  # The umask that will be set for the subcommand.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:87
  def umask; end

  # Set the umask that the subprocess will have. If given as a string, it
  # will be converted to an integer by String#oct.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:204
  def umask=(new_umask); end

  # User the command will run as. Normally set via options passed to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:40
  def user; end

  # User the command will run as. Normally set via options passed to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:40
  def user=(_arg0); end

  # An Array of acceptable exit codes. #error? (and #error!) use this list
  # to determine if the command was successful. Normally set via options to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:58
  def valid_exit_codes; end

  # An Array of acceptable exit codes. #error? (and #error!) use this list
  # to determine if the command was successful. Normally set via options to new
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:58
  def valid_exit_codes=(_arg0); end

  # TODO remove
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:44
  def with_logon; end

  # TODO remove
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:44
  def with_logon=(_arg0); end

  private

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:311
  def parse_options(opts); end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:365
  def validate_options(opts); end
end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:5
class Mixlib::ShellOut::CommandTimeout < ::Mixlib::ShellOut::Error; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:29
Mixlib::ShellOut::DEFAULT_READ_TIMEOUT = T.let(T.unsafe(nil), Integer)

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:7
class Mixlib::ShellOut::EmptyWindowsCommand < ::Mixlib::ShellOut::ShellCommandFailed; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:3
class Mixlib::ShellOut::Error < ::RuntimeError; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:6
class Mixlib::ShellOut::InvalidCommandOption < ::Mixlib::ShellOut::Error; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:28
Mixlib::ShellOut::READ_SIZE = T.let(T.unsafe(nil), Integer)

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout.rb:27
Mixlib::ShellOut::READ_WAIT_TIME = T.let(T.unsafe(nil), Float)

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/exceptions.rb:4
class Mixlib::ShellOut::ShellCommandFailed < ::Mixlib::ShellOut::Error; end

# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:21
module Mixlib::ShellOut::Unix
  # Helper method for sgids
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:41
  def all_seconderies; end

  # The environment variables that are deduced from simulating logon
  # Only valid if login is used
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:63
  def logon_environment; end

  # Merges the two environments for the process
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:74
  def process_environment; end

  # Run the command, writing the command's standard out and standard error
  # to +stdout+ and +stderr+, and saving its exit status object to +status+
  # === Returns
  # returns   +self+; +stdout+, +stderr+, +status+, and +exitstatus+ will be
  # populated with results of the command.
  # === Raises
  # * Errno::EACCES  when you are not privileged to execute the command
  # * Errno::ENOENT  when the command is not available on the system (or not
  #   in the current $PATH)
  # * Chef::Exceptions::CommandTimeout  when the command does not complete
  #   within +timeout+ seconds (default: 600s). When this happens, ShellOut
  #   will send a TERM and then KILL to the entire process group to ensure
  #   that any grandchild processes are terminated. If the invocation of
  #   the child process spawned multiple child processes (which commonly
  #   happens if the command is passed as a single string to be interpreted
  #   by bin/sh, and bin/sh is not bash), the exit status object may not
  #   contain the correct exit code of the process (of course there is no
  #   exit code if the command is killed by SIGKILL, also).
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:96
  def run_command; end

  # The secondary groups that the subprocess will switch to.
  # Currently valid only if login is used, and is set
  # to the user's secondary groups
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:54
  def sgids; end

  # Whether we're simulating a login shell
  #
  # @return [Boolean]
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:36
  def using_login?; end

  # Option validation that is unix specific
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:29
  def validate_options(opts); end

  private

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:279
  def attempt_buffer_read; end

  # Try to reap the child process but don't block if it isn't dead yet.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:408
  def attempt_reap; end

  # Since we call setsid the child_pgid will be the child_pid, set to negative here
  # so it can be directly used in arguments to kill, wait, etc.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:192
  def child_pgid; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:213
  def child_process_status; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:209
  def child_stderr; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:201
  def child_stdin; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:205
  def child_stdout; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:217
  def close_all_pipes; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:250
  def configure_parent_process_file_descriptors; end

  # Replace stdout, and stderr with pipes to the parent, and close the
  # reader side of the error marshaling side channel.
  #
  # If there is no input, close STDIN so when we exec,
  # the new program will know it's never getting input ever.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:229
  def configure_subprocess_file_descriptors; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:318
  def fork_subprocess; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:196
  def initialize_ipc; end

  # Some patch levels of ruby in wide use (in particular the ruby 1.8.6 on OSX)
  # segfault when you IO.select a pipe that's reached eof. Weak sauce.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:267
  def open_pipes; end

  # Attempt to get a Marshaled error from the side-channel.
  # If it's there, un-marshal it and raise. If it's not there,
  # assume everything went well.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:358
  def propagate_pre_exec_failure; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:309
  def read_process_status_to_buffer; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:299
  def read_stderr_to_buffer; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:289
  def read_stdout_to_buffer; end

  # Unconditionally reap the child process. This is used in scenarios where
  # we can be confident the child will exit quickly, and has not spawned
  # and grandchild processes.
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:395
  def reap; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:369
  def reap_errant_child; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:186
  def set_cwd; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:175
  def set_environment; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:162
  def set_group; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:169
  def set_secondarygroups; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:182
  def set_umask; end

  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:155
  def set_user; end

  # @return [Boolean]
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:387
  def should_reap?; end

  # Keep this unbuffered for now
  #
  # source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:272
  def write_to_child_stdin; end
end

# "1.8.7" as a frozen string. We use this with a hack that disables GC to
# avoid segfaults on Ruby 1.8.7, so we need to allocate the fewest
# objects we possibly can.
#
# source://mixlib-shellout-3.2.7/lib/mixlib/shellout/unix.rb:26
Mixlib::ShellOut::Unix::ONE_DOT_EIGHT_DOT_SEVEN = T.let(T.unsafe(nil), String)
