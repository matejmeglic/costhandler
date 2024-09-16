# Costhandler
## Simple Django + VanillaJS templates app

# I was approached by a friend, that would need to track equipment he borrows for event and then produce spec documents that outline what was borrowed and how much equipment is worth. 

### This was the spec:
- user management
- upload pricelists
    - set pricelists as active/inactive to curate what pops on the spec document
- create new spec document
    - extra costs can be on the document
    - different entities that are connected to the pricelist
        - pricelist can have entries that cost 0 EUR, then assign them cost on the spot (like night shift for an associate, you agree for how much they will stay another hour, put that in the extra costs)
        - each spec_entry can have additional person assigned so that we know who brought what and what should be paid to whom
            - breakdown per person provided

### What is not there (MVP):
- payment support
- company data (for proper invoice creation)
- any sort of invoicing/numeration (assumption is this is done in a different software, this is just a quick addendum)
- any sort of company or group user management (every user is a standalone entity)
- Spec sharing (combining seller and buyer so that buyer can check and approve Spec)
- IMPORTANT: Currently, if you delete the pricelist (from the django-admin), you lose all the Spec Item descriptions
- Error handling, tests

### All coded with AI:
- 6h basic structure
- 2h spec entry
- 2h app polishing
